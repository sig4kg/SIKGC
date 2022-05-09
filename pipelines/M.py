import logging

from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.materialize_util import *
import pandas as pd
from scripts import run_scripts
from module_utils.common_util import timethis


class M(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 pipeline_config: PipelineConfig, logger: logging.Logger) -> None:
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
        pred_hrt_df, pred_type_df = materialize(self.pipeline_config.work_dir,
                                                self.context_resource,
                                                self.pipeline_config.reasoner,
                                                exclude_rels=self.pipeline_config.exclude_rels)
        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'm')
        else:
            return self.collect_result(pred_hrt_df, pred_type_df)

    def collect_result(self, pred_hrt_df, pred_type_df):
        train_count = len(self.context_resource.hrt_int_df.index) + self.context_resource.type_count
        context_resource = self.context_resource
        old_type_df = context_resource.type2hrt_int_df()
        new_type_df = pd.concat([pred_type_df, old_type_df, old_type_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        new_type_count = len(new_type_df.index)
        groups = pred_type_df.groupby('head')
        old_ent2types = self.context_resource.entid2classids
        for g in groups:
            ent = g[0]
            types = g[1]['tail'].tolist()
            if ent in old_ent2types:
                old_types = set(old_ent2types[ent])
                new_types = set(types)
                old_ent2types.update({ent: list(old_types | new_types)})
        self.context_resource.type_count = self.context_resource.get_type_count()

        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_rel_count = len(new_hrt_df.index)
        extended_hrt_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(
            keep='first').reset_index(drop=True)
        extend_count = self.context_resource.type_count + len(extended_hrt_df.index)
        new_count = new_type_count + new_rel_count
        context_resource.hrt_int_df = extended_hrt_df
        print("new type assertions: " + str(new_type_count))
        print("new property assertions: " + str(new_rel_count))
        self._log_block_result(new_rel_count, new_rel_count, new_rel_count, "M rel pred - ")
        self._log_block_result(new_type_count, new_type_count, new_type_count, "M type pred - ")
        return train_count, extend_count, new_count, new_count, new_count
