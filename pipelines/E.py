import argparse

from file_util import init_dir
from log_util import get_file_logger
from pipelines.exp_config import *
from pipeline_util import *
from pipelines.ProducerBlock import PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from blp.producer import ex


def run_E_method_without_ACC(work_dir, dataset, model):
    init_dir(work_dir)
    data_conf = DatasetConfig().get_config(dataset)
    blp_conf = BLPConfig().get_blp_config(rel_model=model,
                                          inductive=False,
                                          dataset=dataset,
                                          schema_aware=False,
                                          silver_eval=True,
                                          do_produce=True)
    blp_conf.update({'work_dir': work_dir})
    p_config = PipelineConfig().set_pipeline_config(dataset=dataset,
                                                    loops=1,
                                                    work_dir=work_dir,
                                                    pred_type=False,
                                                    reasoner=None,
                                                    parallel=False,
                                                    pipeline='l',
                                                    produce=True,
                                                    silver_eval=True,
                                                    use_gpu=True)
    p_config.set_blp_config(blp_conf).set_data_config(data_conf)
    context_resource, abox_scanner_scheduler = prepare_context(p_config, consistency_check=False)

    hrt_int_df_2_hrt_blp(context_resource, work_dir,
                         triples_only=False)  # generate all_triples.tsv, entities.txt, relations.txt\
    wait_until_file_is_saved(work_dir + "all_triples.tsv")
    split_data_blp(context_resource=context_resource, work_dir=work_dir, inductive=False,
                      exclude_rels=[])  # split all_triples.tsv to train.tsv, dev.tsv, takes time
    if p_config.silver_eval:
        generate_silver_rel_eval_file(context_resource, work_dir)
    wait_until_blp_data_ready(work_dir, inductive=False)
    # 1. run blp
    ex.run(config_updates=p_config.blp_config)
    wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)

    # 2. consistency checking for new triples
    pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource).drop_duplicates(
        keep='first').reset_index(drop=True)
    print("all produced triples: " + str(len(pred_hrt_df.index)))

    logger = get_file_logger(file_name=p_config.work_dir + f"{p_config.dataset}_{p_config.pipeline}.log")
    new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
        keep=False)
    new_count = len(new_hrt_df.index)
    if new_count == 0:
        logger.info(f"new_count: 0")
        return
    # 3. get valid new triples
    to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(keep="first").reset_index(
        drop=True)
    valids, invalids = abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_rel_IJPs(work_dir=work_dir, save_result=False)
    corrects, incorrects = abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=work_dir, save_result=False)
    new_valids = pd.concat([valids, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
        keep=False)
    new_corrects = pd.concat([corrects, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(
        keep=False)
    new_valid_count = len(new_valids.index)
    new_correct_count = len(new_corrects.index)
    train_count = len(context_resource.hrt_int_df.index)
    logger.info(f"train count: {train_count}; new count: {new_count}; new_valid: {new_valid_count}; new_corrects: {new_correct_count} \n"
                f"correct rate: {new_correct_count  / new_count}, consistent rate:  {new_valid_count / new_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    parser.add_argument('--model', type=str, default="transe")
    parser.add_argument('--dataset', type=str, default="TREAT")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    argss = parser.parse_args()
    run_E_method_without_ACC(argss.work_dir, argss.dataset, argss.model)