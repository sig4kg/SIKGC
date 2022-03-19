from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.anyburl_util import *
import pandas as pd
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler

class AC(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config
        self.work_dir = self.pipeline_config.work_dir
        self.acc = True

    def produce(self, acc=True):
        self.acc = acc
        work_dir = self.work_dir + "A/"
        run_scripts.mk_dir(work_dir)
        context_resource = self.context_resource
        hrt_int_df_2_hrt_anyburl(context_resource, work_dir)
        split_all_triples_anyburl(context_resource, work_dir, exclude_rels=self.pipeline_config.exclude_rels)
        prepare_anyburl_configs(work_dir, pred_with='hr')
        wait_until_anyburl_data_ready(work_dir)
        print("learning anyBURL...")
        run_scripts.learn_anyburl(work_dir)
        print("predicting with anyBURL...")
        run_scripts.predict_with_anyburl(work_dir)
        tmp_pred_hrt1 = read_hrt_pred_anyburl_2_hrt_int_df(work_dir + "predictions/alpha-100",
                                                           context_resource).drop_duplicates(
            keep='first').reset_index(drop=True)
        clean_anyburl_tmp_files(work_dir)
        prepare_anyburl_configs(work_dir, pred_with='rt')
        wait_until_anyburl_data_ready(work_dir)
        print("predicting with anyBURL...")
        run_scripts.predict_with_anyburl(work_dir)
        wait_until_file_is_saved(work_dir + "predictions/alpha-100", 60)
        tmp_pred_hrt2 = read_hrt_pred_anyburl_2_hrt_int_df(work_dir + "predictions/alpha-100",
                                                           context_resource).drop_duplicates(
            keep='first').reset_index(drop=True)
        run_scripts.clean_anyburl(work_dir=work_dir)
        # consistency checking for new triples
        pred_hrt_df = pd.concat([tmp_pred_hrt1, tmp_pred_hrt2]).drop_duplicates(
            keep='first').reset_index(drop=True)

        return self.collect_result(pred_hrt_df)

    def collect_result(self, pred_hrt_df):
        context_resource = self.context_resource
        # acc and collect score
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        if not self.acc:
            tmp_file_name = self.pipeline_config.work_dir + f'subprocess/hrt_a_{os.getpid()}.txt'
            new_hrt_df.to_csv(tmp_file_name, header=False, index=False, sep='\t')
            wait_until_file_is_saved(tmp_file_name)
            del new_hrt_df
            return

        new_count = len(new_hrt_df.index)
        #  backup and clean last round data
        run_scripts.clean_anyburl(work_dir=self.pipeline_config.work_dir)
        to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(keep="first").reset_index(
            drop=True)
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_IJ_patterns(work_dir=self.work_dir)
        corrects = self.abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=self.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_valid_count = len(new_valids.index)
        del new_valids
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_correct_count = len(new_corrects.index)
        del new_corrects
        train_count = len(context_resource.hrt_int_df.index) + context_resource.type_count

        # add new valid hrt to train set
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, valids], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
        extend_count = len(extend_hrt_df.index) + self.context_resource.type_count
        # overwrite train data in context
        context_resource.hrt_int_df = extend_hrt_df
        # check rate
        return train_count, extend_count, new_count, new_valid_count, new_correct_count
