from pipeline_C_L_C import c_l_c
from pipeline_C_anyBURL_C import c_anyburl_c
from pipeline_C_E_C import c_e_c
from pipeline_C_Rumis_C import c_rumis_c
from pipeline_C_M import c_m
from pipeline_CLCACM import clcacm
from pipeline_CLCMCAC import clcmcac
from pipeline_CACMCLC import cacmclc
from pipeline_CACMCEC import cacmcec
from pipeline_CMCLCAC import cmclcac
from scripts import run_scripts
import argparse
from exp_config import *

# by Sylvia Wang

def producers(dataset="TEST", work_dir="../outputs/test/", pipeline="cec", use_gpu=False, loops=3, rel_model="transe", inductive=False):
    run_scripts.mk_dir(work_dir)
    blp_conf = BLPConfig().get_blp_config(rel_model, inductive, dataset)
    data_conf = DatasetConfig().get_config(dataset)
    scores = []
    if pipeline == "cac":
        print("CRC pipeline")
        scores = c_anyburl_c(work_dir=work_dir + f"{pipeline}_{dataset}/",
                             input_dir=data_conf.input_dir,
                             schema_file=data_conf.schema_file,
                             loops=loops,
                             tbox_patterns_dir=data_conf.tbox_patterns_dir,
                             exclude_rels=data_conf.exclude_rels)
    elif pipeline == "cec":
        print("CEC pipeline")
        scores = c_e_c(work_dir=work_dir + f"{pipeline}_{dataset}/",
                       input_dir=data_conf.input_dir,
                       schema_file=data_conf.schema_file,
                       tbox_patterns_dir=data_conf.tbox_patterns_dir,
                       loops=loops,
                       epoch=data_conf.e_max_epoch,
                       exclude_rels=data_conf.exclude_rels,
                       use_gpu=use_gpu)
    elif pipeline == "clc":
        print("CLC pipeline")
        scores = c_l_c(work_dir=work_dir + f"{pipeline}_{dataset}/",
                       input_dir=data_conf.input_dir,
                       schema_file=data_conf.schema_file,
                       tbox_patterns_dir=data_conf.tbox_patterns_dir,
                       loops=loops,
                       exclude_rels=data_conf.exclude_rels,
                       blp_config=blp_conf
                       )
    elif pipeline == "crc":
        print("CRC pipeline")
        scores = c_rumis_c(work_dir=work_dir + f"{pipeline}_{dataset}/",
                           input_dir=data_conf.input_dir,
                           schema_file=data_conf.schema_file,
                           loops=loops,
                           tbox_patterns_dir=data_conf.tbox_patterns_dir)
    elif pipeline == "cm":
        print("CM pipeline")
        scores = c_m(work_dir=work_dir + f"{pipeline}_{dataset}/",
                     input_dir=data_conf.input_dir,
                     schema_file=data_conf.schema_file,
                     loops=1,
                     tbox_patterns_dir=data_conf.tbox_patterns_dir,
                     schema_in_nt=data_conf.schema_in_nt)
    elif pipeline == "clcmcac":
        print("clcmcac pipeline")
        scores = clcmcac(work_dir=work_dir + f"{pipeline}_{dataset}/",
                         input_dir=data_conf.input_dir,
                         schema_file=data_conf.schema_file,
                         tbox_patterns_dir=data_conf.tbox_patterns_dir,
                         loops=loops,
                         exclude_rels=data_conf.exclude_rels,
                         blp_config=blp_conf)
    elif pipeline == "cacmclc":
        print("cacmclc pipeline")
        scores = cacmclc(work_dir=work_dir + f"{pipeline}_{dataset}/",
                         input_dir=data_conf.input_dir,
                         schema_file=data_conf.schema_file,
                         tbox_patterns_dir=data_conf.tbox_patterns_dir,
                         loops=loops,
                         exclude_rels=data_conf.exclude_rels,
                         blp_config=blp_conf,
                         schema_in_nt=data_conf.schema_in_nt)
    elif pipeline == "cacmcec":
        print("cacmcec pipeline")
        scores = cacmcec(work_dir=work_dir + f"{pipeline}_{dataset}/",
                         input_dir=data_conf.input_dir,
                         schema_file=data_conf.schema_file,
                         tbox_patterns_dir=data_conf.tbox_patterns_dir,
                         loops=loops,
                         epoch=data_conf.e_max_epoch,
                         exclude_rels=data_conf.exclude_rels,
                         use_gpu=use_gpu,
                         schema_in_nt=data_conf.schema_in_nt)
    elif pipeline == "cmclcac":
        print("cmclcac pipeline")
        scores = cmclcac(work_dir=work_dir + f"{pipeline}_{dataset}/",
                         input_dir=data_conf.input_dir,
                         schema_file=data_conf.schema_file,
                         tbox_patterns_dir=data_conf.tbox_patterns_dir,
                         loops=loops,
                         exclude_rels=data_conf.exclude_rels,
                         schema_in_nt=data_conf.schema_in_nt)
    elif pipeline == "clcacm":
        print("clcacm pipeline")
        scores = clcacm(work_dir=work_dir + f"{pipeline}_{dataset}/",
                         input_dir=data_conf.input_dir,
                         schema_file=data_conf.schema_file,
                         tbox_patterns_dir=data_conf.tbox_patterns_dir,
                         loops=loops,
                         exclude_rels=data_conf.exclude_rels,
                         schema_in_nt=data_conf.schema_in_nt)
    else:
        print("Unsupported pipeline, please use any of these: cac, cec, crc, cm, cecmcrc, clcmcac.")
        pass
    with open(work_dir + f"{pipeline}_{dataset}.log", encoding='utf-8', mode='w') as out_f:
        for idx, s in enumerate(scores):
            out_f.write(f"loop {idx}:\n")
            for k in s:
                out_f.write(f"{k}: {s[k]} \n")
            out_f.write("-------------\n")
    out_f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    # dataset="TEST", work_dir="outputs/test/", pipeline="cec", use_gpu=False, loops=2
    parser.add_argument('--dataset', type=str, default="TEST")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--pipeline', type=str, default="cm")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=1)
    parser.add_argument("--rel_model", type=str, default="transe")
    parser.add_argument("--inductive", type=bool, default=False)
    args = parser.parse_args()
    producers(dataset=args.dataset,
              work_dir=args.work_dir,
              pipeline=args.pipeline,
              use_gpu=args.use_gpu,
              inductive=args.inductive,
              rel_model=args.rel_model,
              loops=args.loops)
