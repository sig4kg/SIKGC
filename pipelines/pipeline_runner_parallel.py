import pandas as pd
from module_utils.materialize_util import update_ent2class
import log_util
from pipelines.PipelineRunnerBase import *
from pipelines.exp_config import *
from pipeline_util import *
from tqdm.auto import trange
from pathlib import Path
import copy
import multiprocessing


class PipelineRunnerParallel(PipelineRunnerBase):
    block2producer = dict()
    block_names = []
    context_resource = None
    abox_scanner_scheduler = None
    pipeline_config = None

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
        run_scripts.delete_dir(pipeline_config.work_dir)
        init_workdir(pipeline_config.work_dir)
        log_name = pipeline_config.work_dir + f"{''.join(block_names)}_{pipeline_config.dataset}.log"
        log_score(dict(pipeline_config), log_file=log_name)
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
            self.collect_results(get_scores, log_name, idx)
            idx += 1

    # collect results and update context
    def collect_results(self, score_function, log_name, loop_idx):
        old_type_count = self.context_resource.type_count
        train_count = len(self.context_resource.hrt_int_df.index) + old_type_count

        pred_hrt_df, new_ent2types = self.read_tmp_results()
        if len(new_ent2types) > 0:
            new_type_count = update_ent2class(self.context_resource, new_ent2types)
        else:
            new_type_count = 0

        # diff
        new_hrt_df = pd.concat([pred_hrt_df, self.context_resource.hrt_int_df, self.context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_count = len(new_hrt_df.index) + new_type_count
        # del new_hrt_df
        # scan
        to_scan_df = pd.concat([self.context_resource.hrt_int_df, pred_hrt_df], axis=0).drop_duplicates(
            keep='first').reset_index(drop=True)
        # ACC
        valids, invalids = self.abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_rel_IJPs(work_dir=self.pipeline_config.work_dir)
        corrects = self.abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=self.pipeline_config.work_dir)
        #  get scores
        new_valids = pd.concat([valids, self.context_resource.hrt_int_df, self.context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_valid_count = len(new_valids.index) + new_type_count
        # del new_valids
        new_corrects = pd.concat([corrects, self.context_resource.hrt_int_df, self.context_resource.hrt_int_df]).drop_duplicates(
            keep=False)
        new_correct_count = len(new_corrects.index) + new_type_count
        # del new_corrects
        # add new valid hrt to train set
        extend_hrt_df = pd.concat([self.context_resource.hrt_int_df, valids], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
        extend_count = len(extend_hrt_df.index) + self.context_resource.type_count
        # overwrite train data in context
        self.context_resource.hrt_int_df = extend_hrt_df
        s = score_function(train_count, extend_count, new_count, new_valid_count, new_correct_count)
        log_score(s, log_name, loop=loop_idx)

    def read_tmp_results(self):
        pred_hrt_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        ent2types = {}
        subprocess_dir = self.pipeline_config.work_dir + "subprocess/"
        last_round_dir = self.pipeline_config.work_dir + "last_round/"
        files = os.listdir(subprocess_dir)
        for entry in files:
            if entry.startswith("hrt_"):
                tmp_hrt_df = pd.read_csv(subprocess_dir + entry, header=None, names=['head', 'rel', 'tail'], sep="\t").astype('int64')
                pred_hrt_df = pd.concat([pred_hrt_df, tmp_hrt_df]).drop_duplicates(keep='first')
            elif entry.startswith("type_"):
                ent2types = dict()
                with open(subprocess_dir + entry) as f:
                    for l in f.readlines():
                        items = l.strip().split('\t')
                        ent = int(items[0])
                        classes = [int(i) for i in items[1].split('@')]
                        ent2types.update({ent: classes})
            os.system(f"[ -f  {subprocess_dir + entry} ] && mv {subprocess_dir + entry} {last_round_dir}")
        pred_hrt_df = pred_hrt_df.drop_duplicates(keep='first').reset_index(drop=True)
        return pred_hrt_df, ent2types






