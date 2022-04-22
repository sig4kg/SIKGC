from abc import ABC, abstractmethod
import pandas as pd
from module_utils.file_util import wait_until_file_is_saved
from abox_scanner.ContextResources import ContextResources
from pipelines.PipelineConfig import PipelineConfig
import os


class ProducerBlock(ABC):
    def __init__(self, context_resource: ContextResources,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.pipeline_config = pipeline_config
        self.work_dir = self.pipeline_config.work_dir
        self.abox_scanner_scheduler = None

    @abstractmethod
    def produce(self, *args):
        pass

    def _save_result_only(self, pred_hrt_df, pred_type_df, prefix):
        context_resource = self.context_resource
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        tmp_file_name1 = self.pipeline_config.work_dir + f'subprocess/{prefix}_rel_{os.getpid()}.txt'
        new_hrt_df.to_csv(tmp_file_name1, header=False, index=False, sep='\t')
        wait_until_file_is_saved(tmp_file_name1)
        # save type df
        old_type_df = context_resource.type2hrt_int_df()
        new_type_df = pd.concat([pred_type_df, old_type_df, old_type_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        tmp_file_name2 = self.pipeline_config.work_dir + f'subprocess/{prefix}_type_{os.getpid()}.txt'
        new_type_df.to_csv(tmp_file_name2, header=False, index=False, sep='\t')
        wait_until_file_is_saved(tmp_file_name2)
        return

    def _acc_rel_axiom_and_update_context(self, pred_hrt_df):
        context_resource = self.context_resource
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_count = len(new_hrt_df.index)
        to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(keep="first").reset_index(
            drop=True)
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df). \
            scan_rel_IJPs(work_dir=self.work_dir)
        corrects = self.abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=self.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        context_resource.hrt_int_df = valids
        new_valid_count = len(new_valids.index)
        new_correct_count = len(new_corrects.index)
        return new_count, new_valid_count, new_correct_count

    def _acc_type_axiom_and_update_context(self, pred_type_df):
        context_resource = self.context_resource
        old_type_df = context_resource.type2hrt_int_df()
        new_type_df = pd.concat([pred_type_df, old_type_df, old_type_df]).drop_duplicates(
            keep=False).reset_index(drop=True)
        new_count = len(new_type_df.index)
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_type_df(new_type_df). \
            scan_type_IJPs(work_dir=self.work_dir)
        corrects = valids
        groups = valids.groupby('head')
        new_ent2types = dict()
        old_ent2types = self.context_resource.entid2classids
        for g in groups:
            ent = g[0]
            types = g[1]['tail'].tolist()
            if ent in old_ent2types:
                old_types = set(old_ent2types[ent])
                new_types = set(types)
                new_ent2types.update({ent: list(old_types | new_types)})
        new_valid_count = len(valids.index)
        new_correct_count = len(corrects.index)
        return new_count, new_valid_count, new_correct_count

    def _acc_and_collect_result(self, pred_hrt_df, pred_type_df):
        context_resource = self.context_resource
        train_count = len(context_resource.hrt_int_df.index) + context_resource.type_count
        rel_count, rel_valid_count, rel_correct_count = self._acc_rel_axiom_and_update_context(pred_hrt_df)
        type_count, type_valid_count, type_correct_count = self._acc_type_axiom_and_update_context(pred_type_df)
        extend_count = len(context_resource.hrt_int_df.index) + context_resource.type_count
        new_count = rel_count + type_count
        new_valid_count = rel_valid_count + type_valid_count
        new_correct_count = rel_correct_count + type_correct_count
        return train_count, extend_count, new_count, new_valid_count, new_correct_count


