from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from blp.producer import ex
import os
from module_utils.common_util import timethis
from blp.type_producer import type_produce


class LC(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config
        self.work_dir = self.pipeline_config.work_dir
        self.acc = True

    @timethis
    def produce(self, acc=True, pred_type=True):
        self.acc = acc
        work_dir = self.work_dir + "L/"
        prepare_blp(self.work_dir, work_dir)
        mk_dir(work_dir)
        context_resource = self.context_resource
        config = self.pipeline_config
        hrt_int_df_2_hrt_blp(context_resource, work_dir,
                             triples_only=False)  # generate all_triples.tsv, entities.txt, relations.txt\
        wait_until_file_is_saved(work_dir + "all_triples.tsv")
        split_data_blp(context_resource, inductive=config.inductive, work_dir=work_dir,
                       exclude_rels=config.exclude_rels)  # split all_triples.tsv to train.tsv, dev.tsv, takes time
        wait_until_blp_data_ready(work_dir, inductive=config.inductive)
        # 1. run blp rel axiom prediction
        config.blp_config.update({'work_dir': work_dir})
        ex.run(config_updates=config.blp_config)
        wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)

        # 2. consistency checking for new triples
        pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource).drop_duplicates(
            keep='first').reset_index(drop=True)
        print("all produced triples: " + str(len(pred_hrt_df.index)))

        if pred_type:
            df = type_produce(work_dir, context_resource=context_resource)
        return self.collect_result(pred_hrt_df)

    def collect_result(self, pred_hrt_df):
        context_resource = self.context_resource
        abox_scanner_scheduler = self.abox_scanner_scheduler
        config = self.pipeline_config
        # diff
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df,
                                context_resource.hrt_int_df]).drop_duplicates(keep=False)
        if not self.acc:
            tmp_file_name = self.pipeline_config.work_dir + f'subprocess/hrt_l_{os.getpid()}.txt'
            new_hrt_df.to_csv(tmp_file_name, header=False, index=False, sep='\t')
            wait_until_file_is_saved(tmp_file_name)
            del new_hrt_df
            return

        new_count = len(new_hrt_df.index)
        print("all old triples: " + str(len(context_resource.hrt_int_df.index)))
        print("all new triples: " + str(new_count))

        # 3. get valid new triples
        run_scripts.clean_blp(self.work_dir)
        to_scan_df = pd.concat([context_resource.hrt_int_df, new_hrt_df]).drop_duplicates(keep="first").reset_index(
            drop=True)
        valids, invalids = abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_rel_IJPs(work_dir=self.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_valid_count = len(new_valids.index)
        corrects = abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=self.work_dir).drop_duplicates(keep=False)
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_correct_count = len(new_corrects.index)
        del new_corrects
        train_count = len(context_resource.hrt_int_df.index) + self.context_resource.type_count

        # 5. add new valid hrt to train data
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, valids], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
        extend_count = len(extend_hrt_df.index) + self.context_resource.type_count
        context_resource.hrt_int_df = extend_hrt_df
        return train_count, extend_count, new_count, new_valid_count, new_correct_count
