import pandas as pd
from module_utils.materialize_util import update_ent2class
import log_util
from pipelines.PipelineRunnerBase import *
from pipelines.ProducerBlock import ProducerBlock
from pipelines.exp_config import *
from pipeline_util import *
from tqdm.auto import trange
from pathlib import Path
import copy
import multiprocessing


class PipelineRunnerParallel(PipelineRunnerBase, ProducerBlock):
    block2producer = dict()
    block_names = []
    context_resource = None
    abox_scanner_scheduler = None
    pipeline_config = None

    def __init__(self, logger:logging.Logger):
        super().__init__(logger=logger)

    def create_pipeline(self):
        context_resource, abox_scanner_scheduler = prepare_context(self.pipeline_config, consistency_check=True)
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler

        kwargs = {'context_resource': context_resource,
                  'abox_scanner_scheduler':  abox_scanner_scheduler,
                  'pipeline_config': self.pipeline_config}
        for blc in self.block_names:
            block_obj = self.get_block(blc, **kwargs)
            self.block2producer.update({blc: block_obj})

    def run_pipeline(self, pipeline_config:PipelineConfig, block_names=[]):
        self.pipeline_config = pipeline_config
        self.block_names = block_names
        log_score(dict(pipeline_config), logger=self.logger)
        self.create_pipeline()
        get_scores = aggregate_scores()
        idx = 1
        run_scripts.mk_dir(self.pipeline_config.work_dir + "last_round")
        run_scripts.mk_dir(self.pipeline_config.work_dir + "subprocess")
        for ep in trange(pipeline_config.loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
            processes = []
            for block in self.block_names:
                producer = self.block2producer[block]
                # do not apply ACC
                p = multiprocessing.Process(target=producer.produce, args=(False,))
                processes.append(p)
                p.start()
            for p in processes:
                p.join()
            self.collect_results(get_scores, idx)
            idx += 1

    # collect results and update context
    def collect_results(self, score_function, loop_idx):
        old_type_count = self.context_resource.type_count
        pred_hrt_df, pred_type_df = self.read_tmp_results()
        train_count, extend_count, new_count, new_valid_count, new_correct_count = self._acc_and_collect_result(pred_hrt_df, pred_type_df, log_prefix="L")
        s = score_function(train_count, extend_count, new_count, new_valid_count, new_correct_count)
        log_score(s, logger=self.logger, loop=loop_idx)

    def read_tmp_results(self):
        pred_hrt_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        pred_type_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        ent2types = {}
        subprocess_dir = self.pipeline_config.work_dir + "subprocess/"
        last_round_dir = self.pipeline_config.work_dir + "last_round/"
        files = os.listdir(subprocess_dir)
        for entry in files:
            if entry.startswith("hrt_"):
                tmp_hrt_df = pd.read_csv(subprocess_dir + entry, header=None, names=['head', 'rel', 'tail'], sep="\t").astype('int64')
                pred_hrt_df = pd.concat([pred_hrt_df, tmp_hrt_df]).drop_duplicates(keep='first')
            elif entry.startswith("type_"):
                tmp_type_df = pd.read_csv(subprocess_dir + entry, header=None, names=['head', 'rel', 'tail'], sep="\t").astype('int64')
                pred_type_df = pd.concat([pred_type_df, tmp_type_df]).drop_duplicates(keep='first')
            os.system(f"[ -f  {subprocess_dir + entry} ] && mv {subprocess_dir + entry} {last_round_dir}")
        pred_hrt_df = pred_hrt_df.drop_duplicates(keep='first').reset_index(drop=True)
        pred_type_df = pred_type_df.drop_duplicates(keep='first').reset_index(drop=True)
        return pred_hrt_df, pred_type_df

    def produce(self, logger, *args):
        pass






