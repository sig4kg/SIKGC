from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.anyburl_util import *
import pandas as pd
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler


class AC(ProducerBlock):
    def __init__(self, context_resource: ContextResources, abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig) -> None:
        super().__init__(context_resource, pipeline_config)
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.acc = True
        self.pred_type = True

    def produce(self, acc=True, pred_type=True):
        self.acc = acc
        self.pred_type = pred_type
        work_dir = self.work_dir + "A/"
        run_scripts.mk_dir(work_dir)
        context_resource = self.context_resource
        hrt_int_df_2_hrt_anyburl(context_resource, work_dir)
        split_all_triples_anyburl(context_resource, work_dir, exclude_rels=self.pipeline_config.exclude_rels)
        prepare_anyburl_configs(work_dir, pred_with='hr')
        wait_until_anyburl_data_ready(work_dir)
        print("learning anyBURL...")
        run_scripts.learn_anyburl(work_dir)

        def predict_anyburl(pred_with):
            pred_tail_only = pred_with == "type"
            print("predicting with anyBURL " + pred_with)
            run_scripts.predict_with_anyburl(work_dir)
            wait_until_file_is_saved(work_dir + "predictions/alpha-100", 60)
            tmp_pred_hrt = read_hrt_pred_anyburl_2_hrt_int_df(work_dir + "predictions/alpha-100",
                                                              pred_tail_only=pred_tail_only).drop_duplicates(
                keep='first').reset_index(drop=True)
            clean_anyburl_tmp_files(work_dir)
            return tmp_pred_hrt
        # predict
        tmp_pred_hrt1 = predict_anyburl(pred_with='hr')
        clean_anyburl_tmp_files(work_dir)
        prepare_anyburl_configs(work_dir, pred_with='rt')
        tmp_pred_hrt2 = predict_anyburl(pred_with='rt')
        pred_type_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if pred_type:
            prepare_anyburl_configs(work_dir, pred_with='type')
            pred_type_df = predict_anyburl(pred_with='type')

        # clean
        run_scripts.clean_anyburl(work_dir=work_dir)
        pred_hrt_df = pd.concat([tmp_pred_hrt1, tmp_pred_hrt2]).drop_duplicates(
            keep='first').reset_index(drop=True)
        # save result or acc
        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'a')
        else:
            return self._acc_and_collect_result(pred_hrt_df, pred_type_df)


