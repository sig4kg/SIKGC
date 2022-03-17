from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from module_utils.transE_util import *
from module_utils.rumis_util import *


class RC(ProducerBlock):
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.pipeline_config = pipeline_config

    def produce(self):
        work_dir = self.pipeline_config.work_dir
        context_resource = self.context_resource
        config = self.pipeline_config
        hrt_int_df_2_hrt_rumis(context_resource, config.work_dir + "ideal.data.txt")
        wait_until_file_is_saved(config.work_dir + "ideal.data.txt", 120)

        print("running rumis...")
        run_scripts.run_rumis(work_dir)
        check_result = wait_until_file_is_saved(config.work_dir + "DLV/extension.opm.kg.pos.10.needcheck", 60) \
                       and wait_until_file_is_saved(config.work_dir + "DLV/extension.opm.kg.neg.10.needcheck", 60)
        if not check_result:
            print({"no result from rumis producer, check logs"})
            run_scripts.clean_rumis(work_dir=work_dir)
            return -1
        else:
            print("rumis one round done")

        # consistency checking for new triples
        new_hrt_df1 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", context_resource)
        new_hrt_df2 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", context_resource)
        pred_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df1, new_hrt_df2], 0).drop_duplicates(
            keep='first').reset_index(drop=True)

        return self.collect_result(pred_hrt_df)

    def collect_result(self, pred_hrt_df):
        context_resource = self.context_resource
        abox_scanner_scheduler = self.abox_scanner_scheduler
        config = self.pipeline_config
        # diff
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_count = len(new_hrt_df.index)
        del new_hrt_df

        #  backup and clean last round data
        run_scripts.clean_rumis(work_dir=config.work_dir)
        valids, invalids = abox_scanner_scheduler.set_triples_to_scan_int_df(pred_hrt_df).scan_IJ_patterns(
            work_dir=config.work_dir)
        new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_valid_count = len(new_valids.index)
        corrects = abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=config.work_dir)
        new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_correct_count = len(new_corrects.index)
        del new_corrects
        train_count = len(context_resource.hrt_int_df.index)

        # add new valid hrt to train set
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, valids], axis=0).drop_duplicates(keep='first').reset_index(
            drop=True)
        extend_count = len(extend_hrt_df.index)
        # overwrite train data in context
        print("update context data")
        context_resource.hrt_int_df = extend_hrt_df
        return train_count, extend_count, new_count, new_valid_count, new_correct_count
