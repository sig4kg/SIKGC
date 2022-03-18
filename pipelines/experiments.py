from scripts import run_scripts
import argparse
from exp_config import *
from pipelines.pipeline_constructor import *


# by Sylvia Wang

def producers(dataset="TEST", work_dir="../outputs/test/", pipeline="cec", use_gpu=False, loops=1, rel_model="transe",
              inductive=False):
    data_conf = DatasetConfig().get_config(dataset)
    blp_conf = BLPConfig().get_blp_config(rel_model=rel_model, inductive=inductive, dataset=dataset)
    p_config = PipelineConfig().set_config(blp_config=blp_conf,
                                           data_config=data_conf,
                                           dataset=dataset,
                                           loops=loops,
                                           work_dir=work_dir,
                                           use_gpu=use_gpu)
    if pipeline == "cac":
        run_pipeline(p_config, blocks=['AC'])
    elif pipeline == "cec":
        run_pipeline(p_config, blocks=['EC'])
    elif pipeline == "clc":
        run_pipeline(p_config, blocks=['LC'])
    elif pipeline == "crc":
        run_pipeline(p_config, blocks=['RC'])
    elif pipeline == "cm":
        run_pipeline(p_config, blocks=['M'])
    elif pipeline == "clcmcac":
        run_pipeline(p_config, blocks=['LC', 'M', 'AC'])
    elif pipeline == "cacmclc":
        run_pipeline(p_config, blocks=['AC', 'M', 'LC'])
    elif pipeline == "cacmcec":
        run_pipeline(p_config, blocks=['AC', 'M', 'EC'])
    elif pipeline == "cmclcac":
        run_pipeline(p_config, blocks=['M', 'LC', 'AC'])
    elif pipeline == "clcacm":
        run_pipeline(p_config, blocks=['LC', 'AC', 'M'])
    else:
        print("Unsupported pipeline, please use any of these: cac, cec, crc, cm, cecmcrc, clcmcac.")
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    parser.add_argument('--dataset', type=str, default="TREAT")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--pipeline', type=str, default="cac")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=1)
    parser.add_argument("--rel_model", type=str, default="simple")
    parser.add_argument("--inductive", type=bool, default=True)
    args = parser.parse_args()
    producers(dataset=args.dataset,
              work_dir=args.work_dir,
              pipeline=args.pipeline,
              use_gpu=args.use_gpu,
              inductive=args.inductive,
              rel_model=args.rel_model,
              loops=args.loops)
