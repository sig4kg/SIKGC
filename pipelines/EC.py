from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.transE_util import *
import pandas as pd
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from module_utils.transE_util import *
from openKE import train_transe


class EC(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config
        self.acc = True

    def produce(self, acc=True):
        context_resource = self.context_resource
        config = self.pipeline_config
        self.acc = acc
        context_2_hrt_transE(config.work_dir, context_resource, exclude_rels=config.exclude_rels)
        wait_until_train_pred_data_ready(config.work_dir)
        # 1.train transE
        train_transe.train(config.work_dir + "train/", epoch=config.e_max_epoch, use_gpu=config.use_gpu)
        wait_until_file_is_saved(config.work_dir + "checkpoint/transe.ckpt")

        # 2. produce triples
        train_transe.produce(config.work_dir + "train/", config.work_dir + "transE_raw_hrts.txt", use_gpu=config.use_gpu)
        wait_until_file_is_saved(config.work_dir + "transE_raw_hrts.txt", 30)

        # 3. consistency checking for new triples + old triples
        pred_hrt_df = read_hrts_2_hrt_df(config.work_dir + "transE_raw_hrts.txt").drop_duplicates(
            keep='first').reset_index(drop=True)
        return self.collect_result(pred_hrt_df)

    def collect_result(self, pred_hrt_df):
        context_resource = self.context_resource
        # acc and collect score
        abox_scanner_scheduler = self.abox_scanner_scheduler
        config = self.pipeline_config
        # diff
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        if not self.acc:
            tmp_file_name = self.pipeline_config.work_dir + f'subprocess/hrt_e_{os.getpid()}.txt'
            new_hrt_df.to_csv(tmp_file_name, header=False, index=False, sep='\t')
            wait_until_file_is_saved(tmp_file_name)
            return

        new_count = len(new_hrt_df.index)
        # scan
        to_scann_hrt_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df], axis=0).drop_duplicates(
            keep='first').reset_index(drop=True)
        # clean
        run_scripts.clean_tranE(config.work_dir)
        valids, invalids = abox_scanner_scheduler.set_triples_to_scan_int_df(to_scann_hrt_df).scan_rel_IJPs(
            work_dir=config.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_valid_count = len(new_valids.index)
        corrects = abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=config.work_dir)
        # count
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_correct_count = len(new_corrects.index)
        del new_corrects
        train_count = len(context_resource.hrt_int_df.index) + context_resource.type_count

        # 5. add new valid hrt to train data
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, valids], axis=0).drop_duplicates(keep='first').reset_index(
            drop=True)
        extend_count = len(extend_hrt_df.index) + self.context_resource.type_count
        print("update context data")
        context_resource.hrt_int_df = extend_hrt_df
        return train_count, extend_count, new_count, new_valid_count, new_correct_count