import logging

from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from blp.producer import ex
from module_utils.common_util import timethis
from module_utils.type_producer import train_and_produce


class LC(ProducerBlock):
    def __init__(self, context_resource: ContextResources, abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig, logger:logging.Logger) -> None:
        super().__init__(context_resource, abox_scanner_scheduler, pipeline_config, logger)

    @timethis
    def produce(self, acc=True):
        self.acc = acc
        work_dir = self.work_dir + "L/"
        prepare_blp(self.work_dir, work_dir)
        mk_dir(work_dir)
        context_resource = self.context_resource
        config = self.pipeline_config
        inductive=config.blp_config['inductive']
        hrt_int_df_2_hrt_blp(context_resource, work_dir,
                             triples_only=False)  # generate all_triples.tsv, entities.txt, relations.txt\
        wait_until_file_is_saved(work_dir + "all_triples.tsv")
        split_data_blp(context_resource, inductive=inductive, work_dir=work_dir,
                       exclude_rels=config.exclude_rels)  # split all_triples.tsv to train.tsv, dev.tsv, takes time
        if self.pipeline_config.silver_eval:
            generate_silver_rel_eval_file(self.context_resource, work_dir)
        wait_until_blp_data_ready(work_dir, inductive=inductive)
        # 1. run blp rel axiom prediction
        config.blp_config.update({'work_dir': work_dir})
        ex.run(config_updates=config.blp_config)
        pred_hrt_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if config.blp_config['do_produce']:
            wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)
            pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource).drop_duplicates(
            keep='first').reset_index(drop=True)
            print("all produced triples: " + str(len(pred_hrt_df.index)))
        # 2. type prediction
        pred_type_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if self.pipeline_config.pred_type:
            pred_type_df = train_and_produce(work_dir,
                                             context_resource=context_resource, logger=self.logger,
                                             epochs=config.blp_config['max_epochs'], produce=config.blp_config["do_produce"])
        if not config.produce:
            return 0, 0, 0, 0, 0

        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'l')
        else:
            return self.acc_and_collect_result(pred_hrt_df, pred_type_df, log_prefix="L")
