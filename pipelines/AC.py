import logging

from pipelines.PipelineConfig import PipelineConfig
from pipelines.ProducerBlock import ProducerBlock
from module_utils.anyburl_util import *
import pandas as pd
from scripts import run_scripts
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from module_utils.common_util import timethis

class AC(ProducerBlock):
    def __init__(self, context_resource: ContextResources, abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig, logger:logging.Logger) -> None:
        super().__init__(context_resource, pipeline_config, logger)
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.acc = True
        self.tmp_work_dir = pipeline_config.work_dir

    def predict_anyburl(self, pred_with: str):
        pred_tail_only = "type" in pred_with
        print("predicting with anyBURL " + pred_with)
        predict_with_anyburl(self.tmp_work_dir)
        wait_until_file_is_saved(self.tmp_work_dir + "predictions/alpha-100", 60)
        tmp_pred_hrt = read_hrt_pred_anyburl_2_hrt_int_df(self.tmp_work_dir + "predictions/alpha-100",
                                                          pred_tail_only=pred_tail_only).drop_duplicates(
            keep='first').reset_index(drop=True)
        if "type" in pred_with:
            all_classes = self.context_resource.classid2class.keys()
            tmp_pred_hrt = tmp_pred_hrt.query("tail in @all_classes")
        return tmp_pred_hrt

    @timethis
    def produce(self, acc=True):
        self.acc = acc
        work_dir = self.work_dir + "A/"
        self.tmp_work_dir = work_dir
        run_scripts.mk_dir(work_dir)
        context_resource = self.context_resource
        split_all_triples_anyburl(context_resource, work_dir, exclude_rels=self.pipeline_config.exclude_rels)
        prepare_anyburl_configs(work_dir, pred_with='hr')
        wait_until_anyburl_data_ready(work_dir)
        print("learning anyBURL...")
        learn_anyburl(work_dir)
        # predict
        tmp_pred_hrt1 = self.predict_anyburl(pred_with='hr')
        clean_anyburl_tmp_files(self.tmp_work_dir)
        prepare_anyburl_configs(work_dir, pred_with='rt')
        tmp_pred_hrt2 = self.predict_anyburl(pred_with='rt')
        clean_anyburl_tmp_files(self.tmp_work_dir)
        pred_type_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if self.pipeline_config.pred_type:
            prepare_anyburl_configs(work_dir, pred_with='type')
            pred_type_df = self.predict_anyburl(pred_with='type')
            clean_anyburl_tmp_files(self.tmp_work_dir)
        if self.pipeline_config.silver_eval:
            score1, score2 = self.silver_eval()
            self.logger.info(score1)
            self.logger.info(score2)
        # clean
        clean_anyburl(work_dir=work_dir)
        # save result or acc
        pred_hrt_df = pd.concat([tmp_pred_hrt1, tmp_pred_hrt2]).drop_duplicates(
            keep='first').reset_index(drop=True)
        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'a')
        else:
            return self._acc_and_collect_result(pred_hrt_df, pred_type_df, log_prefix="A")

    def silver_eval(self):
        generate_silver_eval_file(context_resource=self.context_resource, anyburl_dir=self.tmp_work_dir)
        # run eval on types
        prepare_anyburl_configs(self.tmp_work_dir, pred_with='type_silver')
        self.predict_anyburl(pred_with='type_silver')
        pred_file = self.tmp_work_dir + "predictions/alpha-100"
        eval_log_file = self.tmp_work_dir + "anyburl_eval.log"
        opt_threshold = get_optimal_threshold(pred_file,
                                              self.context_resource.silver_type,
                                              self.context_resource.classid2class.keys())
        scores1 = get_silver_type_scores(pred_file, self.context_resource.silver_type,
                                         opt_threshold, self.context_resource.classid2class.keys())
        clean_anyburl_tmp_files(self.tmp_work_dir)
        # run eval on rel assertions
        prepare_anyburl_configs(self.tmp_work_dir, pred_with='rel_silver')
        self.predict_anyburl(pred_with='rel_silver')
        scores2 = read_eval_result(self.tmp_work_dir)
        return scores1, scores2








