from pipelines.PipelineRunnerBase import *
from pipeline_util import *
from tqdm.auto import trange


class PipelineRunnerSeries(PipelineRunnerBase):
    blocks = []
    pipeline_config = None

    def __init__(self, logger:logging.Logger):
        super().__init__(logger=logger)

    def create_pipeline(self):
        context_resource, abox_scanner_scheduler = prepare_context(self.pipeline_config, consistency_check=True)
        producer_blocks = []
        kwargs = {'context_resource': context_resource,
                  'abox_scanner_scheduler':  abox_scanner_scheduler,
                  'pipeline_config': self.pipeline_config,
                  'logger': self.logger}
        for blc in self.blocks:
            block_obj = self.get_block(blc, **kwargs)
            producer_blocks.append(block_obj)
        return producer_blocks

    def run_pipeline(self, pipeline_config: PipelineConfig, blocks=[]):
        self.pipeline_config = pipeline_config
        self.blocks = blocks
        log_score(dict(pipeline_config), logger=self.logger)
        producer_blocks = self.create_pipeline()
        get_scores = aggregate_scores()
        idx = 1
        for ep in trange(pipeline_config.loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
            iter_count = add_counts_one_round()
            init_c, extend_c, nc, nv, ncc = 0, 0, 0, 0, 0
            for pdc in producer_blocks:
                a,b,c,d,e = pdc.produce()
                init_c, extend_c, nc, nv, ncc = iter_count(a,b,c,d,e)
            s = get_scores(init_c, extend_c, nc, nv, ncc)
            log_score(s, logger=self.logger, loop=idx)
            idx += 1
            if not pipeline_config.blp_config['inductive']:
                pipeline_config.blp_config['lr'] = pipeline_config.blp_config['lr'] / 2


def add_counts_one_round():
    init_kg, target_kg, nc, vc, cc = [0], [0], [0], [0], [0]

    def add_new(init_kgc, extend_kgc, new_count, new_valid_count, new_correct_count):
        if init_kg[0] == 0:
            init_kg[0] = init_kgc
        target_kg[0] = extend_kgc
        nc[0] += new_count
        vc[0] += new_valid_count
        cc[0] += new_correct_count
        return init_kg[0],target_kg[0], nc[0], vc[0], cc[0]
    return add_new
