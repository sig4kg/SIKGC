from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.materialize_util import *
import pandas as pd
from scripts import run_scripts

class M(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config

    def produce(self):
        self.context_resource.to_ntriples(self.pipeline_config.work_dir, schema_in_nt=self.pipeline_config.schema_in_nt)
        wait_until_file_is_saved(self.pipeline_config.work_dir + "tbox_abox.nt", 120)
        print("running materialization...")
        new_ent2types, new_property_assertions = materialize(self.pipeline_config.work_dir,
                                                             self.context_resource,
                                                             self.abox_scanner_scheduler)
        return self.collect_result(new_ent2types, new_property_assertions)

    def collect_result(self, new_ent2types, new_property_assertions):
        train_count = len(self.context_resource.hrt_int_df.index)
        # merge new types to ent2classes
        new_type_count = update_ent2class(self.context_resource, new_ent2types)
        self.context_resource.new_type_count += new_type_count
        # merge new type assertions
        extended_df = pd.concat([self.context_resource.hrt_int_df, new_property_assertions]).drop_duplicates(
            keep='first').reset_index(drop=True)
        # valids, _ = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_IJ_patterns(self.pipeline_config.work_dir)
        new_valids = pd.concat([extended_df, self.context_resource.hrt_int_df, self.context_resource.hrt_int_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        extend_count = len(extended_df.index) + self.context_resource.new_type_count
        new_count = len(new_valids.index) + new_type_count
        self.context_resource.hrt_int_df = extended_df
        #  backup and clean last round data
        run_scripts.clean_materialization(work_dir=self.pipeline_config.work_dir)
        print("new type assertions: " + str(new_type_count))
        print("new property assertions: " + str(len(new_valids.index)))
        return train_count, extend_count, new_count, new_count, new_count