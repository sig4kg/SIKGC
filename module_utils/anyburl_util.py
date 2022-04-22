from __future__ import annotations
from abox_scanner.ContextResources import ContextResources
from abox_scanner.abox_utils import wait_until_file_is_saved, save_to_file
import os
import os.path as osp
from itertools import zip_longest
import pandas as pd
import random
from module_utils.schema_silver_sample import *
from module_utils.sample_util import *


def read_hrt_pred_anyburl_2_hrt_int_df(pred_anyburl_file, pred_tail_only=False) -> pd.DataFrame:
    with open(pred_anyburl_file) as f:
        lines = f.readlines()
        chunks = zip_longest(*[iter(lines)] * 3, fillvalue='')
        all_preds = []
        for chunk in chunks:
            tmp_preds = []
            original_triple = chunk[0].strip().split()
            h = original_triple[0]
            r = original_triple[1]
            t = original_triple[2]
            pred_t = chunk[2][7:].strip().split('\t')
            pred_ts = zip_longest(*[iter(pred_t)] * 2, fillvalue='')  # preds and scores
            tmp_preds.extend([[ph[0], r, t] for ph in pred_hs if ph[0] != ''])
            if not pred_tail_only:
                pred_h = chunk[1][7:].strip().split('\t')
                pred_hs = zip_longest(*[iter(pred_h)] * 2, fillvalue='')  # preds and scores
                tmp_preds.extend([[h, r, pt[0]] for pt in pred_ts if pt[0] != ''])
            all_preds.extend(tmp_preds)
    df = pd.DataFrame(data=all_preds, columns=['head', 'rel', 'tail'])
    df = df.drop_duplicates(keep='first')
    df = df.astype(int)
    return df


def hrt_int_df_2_hrt_anyburl(context_resource: ContextResources, anyburl_dir):
    df = context_resource.hrt_int_df
    df.to_csv(anyburl_dir + "all_triples.txt", index=False, header=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir + "all_triples.txt")


def type2hrt_int_df(type_dict) -> pd.DataFrame:
    type_hrt = []
    for entid in type_dict:
        h = entid
        r = 0
        typeOfe = type_dict[entid]
        ent_type_hrt = [[h, r, t] for t in typeOfe]
        type_hrt.extend(ent_type_hrt)
    type_df = pd.DataFrame(data=type_hrt, columns=['head', 'rel', 'tail'])
    return type_df


def split_all_triples_anyburl(context_resource: ContextResources, anyburl_dir, exclude_rels=[], exclude_ents=[]):
    df_rel_train, df_rel_dev, df_rel_test = split_relation_triples(context_resource=context_resource,
                                                                   exclude_rels=exclude_rels,
                                                                   produce=True)
    dict_type_train, dict_type_dev, dict_type_test = split_type_triples(context_resource=context_resource,
                                                                  exclude_ents=exclude_ents,
                                                                  produce=True)
    df_type_train = type2hrt_int_df(dict_type_train)
    df_type_dev = type2hrt_int_df(dict_type_dev)
    df_train = pd.concat([df_rel_train, df_type_train]).reset_index(drop=True)
    df_dev = pd.concat([df_rel_dev, df_type_dev]).reset_index(drop=True)
    df_hr = df_rel_test.drop_duplicates(['head', 'rel'], keep='first')
    df_rt = df_rel_test.drop_duplicates(['rel', 'tail'], keep='first')
    if len(df_hr.index) > len(df_rt.index):
        df_hr = pd.concat([df_hr, df_rt, df_rt]).drop_duplicates(keep=False)
    else:
        df_rt = pd.concat([df_rt, df_hr, df_hr]).drop_duplicates(keep=False)

    df_train.to_csv(osp.join(anyburl_dir, f'train.txt'), header=False, index=False, sep='\t')
    df_dev.to_csv(osp.join(anyburl_dir, f'valid.txt'), header=False, index=False, sep='\t')
    df_test_type = type2hrt_int_df(dict_type_test).drop_duplicates(['head'], keep='first')
    df_hr.to_csv(osp.join(anyburl_dir, f'test_hr.txt'), header=False, index=False, sep='\t')
    df_rt.to_csv(osp.join(anyburl_dir, f'test_rt.txt'), header=False, index=False, sep='\t')
    df_test_type.to_csv(osp.join(anyburl_dir, f'test_type.txt'), header=False, index=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir+'train.txt')
    wait_until_file_is_saved(anyburl_dir+'valid.txt')
    wait_until_file_is_saved(anyburl_dir+'test_hr.txt')
    wait_until_file_is_saved(anyburl_dir+'test_rt.txt')
    wait_until_file_is_saved(anyburl_dir+'test_type.txt')


def prepare_anyburl_configs(anyburl_dir, pred_with='hr'):
    config_apply = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_TEST      = {anyburl_dir}test_{pred_with}.txt\n" \
                   f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                   f"PATH_RULES     = {anyburl_dir}rules/alpha-100\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}predictions/alpha-100\n" \
                   "UNSEEN_NEGATIVE_EXAMPLES = 5\n" \
                   "TOP_K_OUTPUT = 10\n"\
                   "WORKER_THREADS = 7"
    config_eval = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                  f"PATH_TEST      = {anyburl_dir}test_{pred_with}.txt\n" \
                  f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                  f"PATH_PREDICTIONS   = {anyburl_dir}predictions/alpha-100"
    config_learn = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}rules/alpha\n" \
                   f"SNAPSHOTS_AT = 100\n" \
                   f"WORKER_THREADS = 4\n"
    save_to_file(config_apply, anyburl_dir + "config-apply.properties")
    save_to_file(config_eval, anyburl_dir + "config-eval.properties")
    save_to_file(config_learn, anyburl_dir + "config-learn.properties")


def clean_anyburl_tmp_files(anyburl_dir):
    os.system(f"[ -d {anyburl_dir}predictions ] && rm {anyburl_dir}predictions/*")
    os.system(f"[ -f {anyburl_dir}config-apply.properties ] && rm {anyburl_dir}config-apply.properties")

def wait_until_anyburl_data_ready(anyburl_dir):
    wait_until_file_is_saved(anyburl_dir + "test_hr.txt")
    wait_until_file_is_saved(anyburl_dir + "test_rt.txt")
    wait_until_file_is_saved(anyburl_dir + "valid.txt")
    wait_until_file_is_saved(anyburl_dir + "train.txt")
    wait_until_file_is_saved(anyburl_dir + "config-apply.properties")
    wait_until_file_is_saved(anyburl_dir + "config-eval.properties")
    wait_until_file_is_saved(anyburl_dir + "config-learn.properties")


if __name__ == "__main__":
    read_hrt_pred_anyburl_2_hrt_int_df("../outputs/treat/anyburl/predictions/alpha-100")
