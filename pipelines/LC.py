import logging

import file_util
from pipelines.ProducerBlock import ProducerBlock, PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from blp.producer import ex
from module_utils.common_util import timethis
from module_utils.type_producer import train_and_produce


class LC(ProducerBlock):
    def __init__(self, context_resource: ContextResources, abox_scanner_scheduler: AboxScannerScheduler,
                 pipeline_config: PipelineConfig, logger: logging.Logger) -> None:
        super().__init__(context_resource, abox_scanner_scheduler, pipeline_config, logger)

    @timethis
    def produce(self, acc=True):
        self.acc = acc
        work_dir = self.work_dir + "L/"
        self.pipeline_config.blp_config.update({'work_dir': work_dir})
        prepare_blp(self.work_dir, work_dir)
        mk_dir(work_dir)
        context_resource = self.context_resource
        config = self.pipeline_config
        inductive = config.blp_config['inductive']
        clean_blp(work_dir)
        hrt_int_df_2_hrt_blp(context_resource, work_dir,
                             triples_only=False)  # generate all_triples.tsv, entities.txt, relations.txt\
        wait_until_file_is_saved(work_dir + "all_triples.tsv")
        split_data_blp(context_resource, inductive=inductive, work_dir=work_dir,
                       exclude_rels=config.exclude_rels)  # split all_triples.tsv to train.tsv, dev.tsv, takes time

        if self.pipeline_config.silver_eval:
            self.silver_eval_prepare()

        if config.blp_config['schema_aware']:
            self.schema_aware_sampling_prepare()

        wait_until_blp_data_ready(work_dir, inductive=inductive)
        # 1. run blp rel axiom prediction
        ex.run(config_updates=config.blp_config)
        pred_hrt_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if config.produce:
            wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)
            pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv",
                                                     context_resource).drop_duplicates(
                keep='first').reset_index(drop=True)
            print("all produced triples: " + str(len(pred_hrt_df.index)))
        # 2. type prediction
        pred_type_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if self.pipeline_config.pred_type:
            pred_type_df = train_and_produce(work_dir,
                                             context_resource=context_resource, logger=self.logger,
                                             train_batch_size=512,
                                             epochs=config.blp_config['max_epochs'],
                                             produce=config.blp_config["do_produce"])
        if not config.produce:
            return
        if not acc:
            return self._save_result_only(pred_hrt_df, pred_type_df, 'l')
        else:
            return self.acc_and_collect_result(pred_hrt_df, pred_type_df, log_prefix="L")

    def silver_eval_prepare(self):
        work_dir = self.work_dir + "L/"
        generate_silver_rel_eval_file(self.context_resource, work_dir)

    def schema_aware_sampling_prepare(self):
        work_dir = self.work_dir + "L/"
        config = self.pipeline_config
        context_resource = self.context_resource
        if not file_util.does_file_exist(self.work_dir + "invalid_hrt.txt") and config.silver_eval:
            config.blp_config.update({'schema_aware': False, 'do_produce': True, 'silver_eval': False})
            ex.run(config_updates=config.blp_config)
            wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)
            pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv",
                                                     context_resource).drop_duplicates(
                keep='first').reset_index(drop=True)
            to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(
                keep="first").reset_index(
                drop=True)
            _, similar_inv = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df). \
                scan_rel_IJPs(work_dir=self.work_dir, save_result=True)
            config.blp_config.update({'schema_aware': True, 'do_produce': config.produce, 'silver_eval': config.silver_eval})
        elif file_util.does_file_exist(self.work_dir + "invalid_hrt.txt"):
            similar_inv = file_util.read_hrt_2_hrt_int_df(self.work_dir + "invalid_hrt.txt")
        else:
            similar_inv = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])

        neg_examples = similar_inv.drop_duplicates(keep='first')
        # blp need the uris
        neg_examples[['head', 'tail']] = neg_examples[['head', 'tail']].applymap(
            lambda x: self.context_resource.id2ent[x])  # to uri
        neg_examples['rel'] = neg_examples['rel'].apply(
            lambda x: self.context_resource.id2op[x])  # to uri
        neg_examples.to_csv(f"{work_dir}neg_examples.txt", header=False, index=False, sep='\t', mode='w')

