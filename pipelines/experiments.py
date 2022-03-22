from scripts import run_scripts
import argparse
from exp_config import *
from pipelines.pipeline_runner_series import *
from pipelines.pipeline_runner_parallel import *
import torch

# by Sylvia Wang

def get_block_names(name_in_short: str):
    capital_names = name_in_short.upper().strip().split('_')
    supported = ['M', 'A', 'L']
    if any([x not in supported for x in capital_names]):
        print("Unsupported pipeline, please use pipeline names as a_l_m, m_a_l etc.")
        return []
    else:
        return capital_names



def producers(dataset="TEST", work_dir="../outputs/test/", pipeline="clc", use_gpu=False, loops=1, rel_model="transe",
              inductive=False, schema_in_nt='', parallel=False):
    data_conf = DatasetConfig().get_config(dataset)
    blp_conf = BLPConfig().get_blp_config(rel_model=rel_model, inductive=inductive, dataset=dataset)
    p_config = PipelineConfig().set_config(blp_config=blp_conf,
                                           data_config=data_conf,
                                           dataset=dataset,
                                           loops=loops,
                                           work_dir=work_dir,
                                           use_gpu=use_gpu)
    if schema_in_nt != '':
        p_config.schema_in_nt = schema_in_nt
    if parallel:
        pipeline_runner = PipelineRunnerParallel()
    else:
        pipeline_runner = PipelineRunnerSeries()
    block_names = get_block_names(pipeline)
    if len(block_names) == 0:
        return
    else:
        pipeline_runner.run_pipeline(p_config, block_names)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    parser.add_argument('--dataset', type=str, default="TEST")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--pipeline', type=str, default="l")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=1)
    parser.add_argument("--rel_model", type=str, default="rotate")
    parser.add_argument("--inductive", type=bool, default=False)
    parser.add_argument("--schema_in_nt", type=str, default='')
    parser.add_argument("--parallel", type=bool, default=False)
    args = parser.parse_args()
    if args.parallel:
        torch.multiprocessing.set_start_method('spawn')
    producers(dataset=args.dataset,
              work_dir=args.work_dir,
              pipeline=args.pipeline,
              use_gpu=args.use_gpu,
              inductive=args.inductive,
              rel_model=args.rel_model,
              loops=args.loops,
              schema_in_nt=args.schema_in_nt,
              parallel=args.parallel)
