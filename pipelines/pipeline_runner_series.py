from pipelines.PipelineRunnerBase import *
from pipeline_util import *
from tqdm.auto import trange


class PipelineRunnerSeries(PipelineRunnerBase):
    pipeline_config = None

    def __init__(self, pipeline_config: PipelineConfig, logger:logging.Logger):
        super().__init__(logger=logger)
        self.pipeline_config = pipeline_config
        self.context_resource: ContextResources = None

    def create_pipeline(self):
        self.context_resource, abox_scanner_scheduler = prepare_context(self.pipeline_config)
        producer_blocks = []
        kwargs = {'context_resource': self.context_resource,
                  'abox_scanner_scheduler':  abox_scanner_scheduler,
                  'pipeline_config': self.pipeline_config,
                  'logger': self.logger}
        block_names = get_block_names(self.pipeline_config.pipeline)
        for blc in block_names:
            block_obj = self.get_block(blc, **kwargs)
            producer_blocks.append(block_obj)
        return producer_blocks

    def run_pipeline(self):
        log_score(dict(self.pipeline_config), logger=self.logger)
        producer_blocks = self.create_pipeline()
        get_scores = aggregate_scores()
        idx = 1
        for ep in trange(self.pipeline_config.loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
            iter_count = add_counts_one_round()
            init_c, extend_c, nc, nv, ncc = 0, 0, 0, 0, 0
            for pdc in producer_blocks:
                if not self.pipeline_config.produce:
                    pdc.produce()
                else:
                    a,b,c,d,e = pdc.produce()
                    init_c, extend_c, nc, nv, ncc = iter_count(a,b,c,d,e)
            if not self.pipeline_config.produce:
                continue
            s = get_scores(init_c, extend_c, nc, nv, ncc)
            log_score(s, logger=self.logger, loop=idx)
            idx += 1
            if not self.pipeline_config.blp_config['inductive']:
                self.pipeline_config.blp_config['lr'] = self.pipeline_config.blp_config['lr'] / 2
        if self.pipeline_config.to_nt:
            self.context_resource.df2nt(self.context_resource.hrt_int_df,
                                        self.pipeline_config.work_dir)


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
