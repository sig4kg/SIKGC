import logging
import pandas as pd
from module_utils.file_util import wait_until_file_is_saved
from abox_scanner.ContextResources import ContextResources
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from pipelines.PipelineConfig import PipelineConfig
import os


class ProducerBlock():
    def __init__(self, context_resource: ContextResources, abox_scanner_scheduler:AboxScannerScheduler,
                 pipeline_config: PipelineConfig, logger: logging.Logger) -> None:
        self.context_resource = context_resource
        self.pipeline_config = pipeline_config
        self.work_dir = self.pipeline_config.work_dir
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.logger = logger
        self.acc = True

    def produce(self, logger, *args):
        pass

    def _save_result_only(self, pred_hrt_df, pred_type_df, prefix):
        context_resource = self.context_resource
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        tmp_file_name1 = self.pipeline_config.work_dir + f'subprocess/rel_{prefix}_{os.getpid()}.txt'
        new_hrt_df.to_csv(tmp_file_name1, header=False, index=False, sep='\t')
        wait_until_file_is_saved(tmp_file_name1)
        # save type df
        old_type_df = context_resource.type2hrt_int_df()
        new_type_df = pd.concat([pred_type_df, old_type_df, old_type_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        tmp_file_name2 = self.pipeline_config.work_dir + f'subprocess/type_{prefix}_{os.getpid()}.txt'
        new_type_df.to_csv(tmp_file_name2, header=False, index=False, sep='\t')
        wait_until_file_is_saved(tmp_file_name2)
        return

    def _acc_rel_axiom_and_update_context(self, pred_hrt_df):
        context_resource = self.context_resource
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_count = len(new_hrt_df.index)
        if new_count == 0:
            return 0, 0, 0
        to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(keep="first").reset_index(
            drop=True)
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df). \
            scan_rel_IJPs(work_dir=self.work_dir)
        corrects, incorrects = self.abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=self.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        context_resource.hrt_int_df = corrects
        new_valid_count = len(new_valids.index)
        new_correct_count = len(new_corrects.index)
        return new_count, new_valid_count, new_correct_count

    def _acc_type_axiom_and_update_context(self, pred_type_df):
        if len(pred_type_df.index) == 0:
            return 0, 0, 0
        context_resource = self.context_resource
        old_type_df = context_resource.type2hrt_int_df()
        new_type_df = pd.concat([pred_type_df, old_type_df, old_type_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        new_count = len(new_type_df.index)
        if new_count == 0:
            return 0, 0, 0
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_type_df(new_type_df). \
            scan_type_IJPs(work_dir=self.work_dir)
        corrects = valids
        self._update_ent2classes(valids)
        new_valid_count = len(valids.index)
        new_correct_count = len(corrects.index)
        return new_count, new_valid_count, new_correct_count

    def _update_ent2classes(self, type_df):
        groups = type_df.groupby('head')
        old_ent2types = self.context_resource.entid2classids
        for g in groups:
            ent = g[0]
            types = g[1]['tail'].tolist()
            if ent in old_ent2types:
                old_types = set(old_ent2types[ent])
                new_types = set(types)
                old_ent2types.update({ent: list(old_types | new_types)})

    def acc_and_collect_result(self, pred_hrt_df, pred_type_df, log_prefix=""):
        context_resource = self.context_resource
        train_count = len(context_resource.hrt_int_df.index) + context_resource.get_type_count()
        # train_count = train_count if self.pipeline_config.pred_type else len(context_resource.hrt_int_df.index)
        rel_count, rel_valid_count, rel_correct_count = self._acc_rel_axiom_and_update_context(pred_hrt_df)
        type_count, type_valid_count, type_correct_count = self._acc_type_axiom_and_update_context(pred_type_df)
        extend_count = len(context_resource.hrt_int_df.index) + context_resource.get_type_count()
        # extend_count = extend_count if self.pipeline_config.pred_type else len(context_resource.hrt_int_df.index)
        new_count = rel_count + type_count
        new_valid_count = rel_valid_count + type_valid_count
        new_correct_count = rel_correct_count + type_correct_count
        self._log_block_result(rel_count, rel_valid_count, rel_correct_count, f"{log_prefix} rel pred")
        self._log_block_result(type_count, type_valid_count, type_correct_count, f"{log_prefix} type pred")
        return train_count, extend_count, new_count, new_valid_count, new_correct_count

    def _log_block_result(self, new_count, valid_count, correct_count, prefix=''):
        log_str = f"Block {prefix} tmp results -  new: {new_count}, valid: {valid_count}, correct: {correct_count}"
        self.logger.info(log_str)
