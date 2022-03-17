import log_util
from pipelines.exp_config import *
from pipeline_util import *
import pipelines.M
import pipelines.RC
import pipelines.AC
import pipelines.LC
import pipelines.EC
from tqdm.auto import trange
from pathlib import Path


def add_counts():
    init_kg, target_kg, nc, vc, cc = [0], [0], [0], [0], [0]
    def add_new(init_kgc, extend_kgc, new_count, new_valid_count, new_correct_count):
        init_kg[0] = init_kgc
        target_kg[0] = extend_kgc
        nc[0] += new_count
        vc[0] += new_valid_count
        cc[0] +=  new_correct_count
        return init_kg[0],target_kg[0], nc[0], vc[0], cc[0]
    return add_new


def log_score(json_data, loop, log_file):
    with open(log_file, encoding='utf-8', mode='w') as out_f:
        for idx, s in enumerate(json_data):
            out_f.write(f"loop {loop}:\n")
            for k in s:
                out_f.write(f"{k}: {s[k]} \n")
            out_f.write("-------------\n")
    out_f.close()

def create_pipeline(pipeline_config:PipelineConfig, blocks= []):
    letter2block = {
        'M': pipelines.M.M,
        'LC': pipelines.LC.LC,
        'AC': pipelines.AC.AC,
        'EC': pipelines.EC.EC
    }
    context_resource, abox_scanner_scheduler = prepare_context(pipeline_config, consistency_check=True,
                    create_id_file=False)
    producer_blocks = []
    for blc in blocks:
        block_obj = letter2block[blc](context_resource, abox_scanner_scheduler, pipeline_config)
        producer_blocks.append(block_obj)
    return producer_blocks


def run_pipeline(pipeline_config:PipelineConfig, blocks=[]):
    producer_blocks = create_pipeline(pipeline_config, blocks)
    get_scores = aggregate_scores()
    log_name = pipeline_config.work_dir + f"{''.join(blocks)}_{pipeline_config.dataset}.log"
    idx = 1
    for ep in trange(pipeline_config.loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        iter_count = add_counts()
        init_c, extend_c, nc, nv, ncc = 0, 0, 0, 0, 0
        for pdc in producer_blocks:
            a,b,c,d,e = pdc.produce()
            init_c, extend_c, nc, nv, ncc = iter_count(a,b,c,d,e)
        s = get_scores(init_c, extend_c, nc, nv, ncc)
        log_score(s, idx, log_name)
        idx += 1


if __name__ == "__main__":
    l_conf = BLPConfig().get_blp_config(rel_model='transe', inductive=False, dataset='TEST')
    d_conf = DatasetConfig().get_config(dataset='TEST')
    p_config = PipelineConfig()
    p_config.set_config(blp_config=l_conf,
                        data_config=d_conf,
                        dataset='TEST',
                        loops=2,
                        work_dir='../outputs/test/',
                        use_gpu=False)
    run_pipeline(p_config, blocks=['M', 'LC', 'AC'])

