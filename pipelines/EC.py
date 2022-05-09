import logging

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
                 pipeline_config: PipelineConfig, logger:logging.Logger) -> None:
        super().__init__(context_resource, pipeline_config, logger)
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config
        self.acc = True

    def produce(self, acc=True, pred_type=False):
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
        train_count = len(context_resource.hrt_int_df.index) + context_resource.get_type_count()
        rel_count, rel_valid_count, rel_correct_count = self._acc_rel_axiom_and_update_context(pred_hrt_df)
        extend_count = len(context_resource.hrt_int_df.index) + context_resource.get_type_count()
        self._log_block_result(rel_count, rel_valid_count, rel_correct_count, f"E rel pred - ")
        return train_count, extend_count, rel_count, rel_valid_count, rel_correct_count
