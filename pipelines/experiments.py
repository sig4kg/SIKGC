from file_util import init_dir
from pipelines.exp_config import DatasetConfig, BLPConfig
from scripts import run_scripts
import argparse
from log_util import get_file_logger
from pipelines.pipeline_runner_series import *
from pipelines.pipeline_runner_parallel import *
import torch

# by Sylvia Wang

def producers(pipeline_config: PipelineConfig):
    block_names = get_block_names(pipeline_config.pipeline)
    if len(block_names) == 0:
        return
    run_scripts.delete_dir(pipeline_config.work_dir)
    init_dir(pipeline_config.work_dir)
    logger = get_file_logger(file_name=pipeline_config.work_dir + f"{pipeline_config.dataset}_{pipeline_config.pipeline}.log")
    if pipeline_config.parallel:
        pipeline_runner = PipelineRunnerParallel(pipeline_config, logger=logger)
    else:
        pipeline_runner = PipelineRunnerSeries(pipeline_config, logger=logger)
    pipeline_runner.run_pipeline()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    parser.add_argument('--dataset', type=str, default="DB15K")
    parser.add_argument('--work_dir', type=str, default="../outputs/db15k/")
    parser.add_argument('--pipeline', type=str, default="a")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=1)
    parser.add_argument("--rel_model", type=str, default="complex", choices=['complex', 'transe', 'distmult', 'simple'])
    parser.add_argument("--inductive", type=str, default='False')
    parser.add_argument("--schema_in_nt", type=str, default='tbox.nt')
    parser.add_argument("--parallel", type=str, default='False')
    parser.add_argument("--schema_aware_sampling", type=str, default='False', help="A schema-aware negative sampling strategy.")
    parser.add_argument("--pre_negs", type=str, default='False', help="Use pre generated schema-consistent negatives, only active with schema_aware_sampling")
    parser.add_argument("--bernoulli", type=str, default='False', help="Bernoulli distribution sampling, do not use with schema-aware sampling")
    parser.add_argument("--reasoner", type=str, default='Konclude', choices=['Konclude', 'TrOWL'])
    parser.add_argument("--pred_type", type=str, default='False')
    parser.add_argument("--silver_eval", type=str, default='True')
    parser.add_argument("--produce", type=str, default='True')
    parser.add_argument("--start_acc", type=str, default='False', help="Whether exclude schema-inconsistent triples from original KG.")
    parser.add_argument("--use_checkpoint", type=str, default='False')
    parser.add_argument("--to_nt", type=str, default='True', help="save expanded KG to nt file.")

    args = parser.parse_args()
    if args.parallel:
        torch.multiprocessing.set_start_method('spawn')
    data_conf = DatasetConfig().get_config(args.dataset)
    if args.schema_in_nt != '':
        data_conf.schema_in_nt = args.schema_in_nt
    blp_conf = BLPConfig().get_blp_config(rel_model=args.rel_model,
                                          inductive=args.inductive == 'True',
                                          dataset=args.dataset,
                                          schema_aware=args.schema_aware_sampling == 'True',
                                          pre_negs=args.pre_negs == "True",
                                          silver_eval=args.silver_eval == 'True',
                                          use_checkpoint=args.use_checkpoint == 'True',
                                          bernoulli=args.bernoulli == 'True',
                                          do_produce=args.produce == 'True')
    p_config = PipelineConfig().set_pipeline_config(dataset=args.dataset,
                                                    loops=args.loops,
                                                    work_dir=args.work_dir,
                                                    pred_type=args.pred_type == 'True',
                                                    reasoner=args.reasoner,
                                                    parallel=args.parallel == 'True',
                                                    pipeline=args.pipeline,
                                                    use_gpu=args.use_gpu,
                                                    silver_eval=args.silver_eval == 'True',
                                                    start_acc=args.start_acc == 'True',
                                                    produce=args.produce == 'True',
                                                    to_nt=args.to_nt=='True')
    p_config.set_blp_config(blp_conf).set_data_config(data_conf)
    producers(p_config)
