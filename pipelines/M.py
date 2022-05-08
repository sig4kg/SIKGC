import logging

from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.materialize_util import *
import pandas as pd
from scripts import run_scripts
from module_utils.common_util import timethis

class M(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 pipeline_config: PipelineConfig, logger:logging.Logger) -> None:
        super().__init__(context_resource, pipeline_config, logger)
        self.context_resource = context_resource
        self.pipeline_config = pipeline_config
        self.acc = True

    # if ACC=False, it means running in parallel, we do ACC until all producers complete.
    @timethis
    def produce(self, acc=True):
        self.acc = acc
        self.context_resource.to_ntriples(self.pipeline_config.work_dir, schema_in_nt=self.pipeline_config.schema_in_nt)
        wait_until_file_is_saved(self.pipeline_config.work_dir + "tbox_abox.nt", 120)
        print("running materialization...")
        pred_type_df, pred_hrt_df = materialize(self.pipeline_config.work_dir,
                                                             self.context_resource,
                                                             self.pipeline_config.reasoner,
                                                             exclude_rels=self.pipeline_config.exclude_rels)
        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'm')
        else:
            return self.collect_result(pred_hrt_df, pred_type_df)

    def collect_result(self, new_property_assertions, new_ent2types):
        train_count = len(self.context_resource.hrt_int_df.index) + self.context_resource.type_count
        # merge new types to ent2classes
        new_type_count = update_ent2class(self.context_resource, new_ent2types)
        # merge new type assertions
        extended_df = pd.concat([self.context_resource.hrt_int_df, new_property_assertions]).drop_duplicates(
            keep='first').reset_index(drop=True)
        new_valids = pd.concat([extended_df, self.context_resource.hrt_int_df, self.context_resource.hrt_int_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        extend_count = len(extended_df.index) + self.context_resource.type_count
        new_rel_count = len(new_valids.index)
        new_count = new_rel_count + new_type_count
        self.context_resource.hrt_int_df = extended_df
        #  backup and clean last round data
        run_scripts.clean_materialization(work_dir=self.pipeline_config.work_dir)
        print("new type assertions: " + str(new_type_count))
        print("new property assertions: " + str(len(new_valids.index)))
        self._log_block_result(new_rel_count, new_rel_count, new_rel_count, "M rel pred - ")
        self._log_block_result(new_type_count, new_type_count, new_type_count, "M type pred - ")
        return train_count, extend_count, new_count, new_count, new_count