from __future__ import annotations
from abox_scanner.ContextResources import ContextResources
from abox_scanner.abox_utils import wait_until_file_is_saved, save_to_file
import os
import os.path as osp
from itertools import zip_longest
import pandas as pd
import random


def read_hrt_pred_anyburl_2_hrt_int_df(pred_anyburl_file, context_resource: ContextResources) -> pd.DataFrame:
    with open(pred_anyburl_file) as f:
        lines = f.readlines()
        chunks = zip_longest(*[iter(lines)] * 3, fillvalue='')
        all_preds = []
        for chunk in chunks:
            tmp_preds = []
            original_triple = chunk[0].strip().split()
            pred_h = chunk[1][7:].strip().split('\t')
            pred_t = chunk[2][7:].strip().split('\t')
            h = original_triple[0]
            r = original_triple[1]
            t = original_triple[2]
            # preds and scores
            pred_hs = zip_longest(*[iter(pred_h)] * 2, fillvalue='')
            pred_ts = zip_longest(*[iter(pred_t)] * 2, fillvalue='')
            tmp_preds.extend([[ph[0], r, t] for ph in pred_hs if ph[0] != ''])
            tmp_preds.extend([[h, r, pt[0]] for pt in pred_ts if pt[0] != ''])

            # tmp_preds = [[context_resource.ent2id[i[0]],
            #               context_resource.rel2id[i[1]],
            #               context_resource.ent2id[i[2]]] for i in tmp_preds]
            all_preds.extend(tmp_preds)
    df = pd.DataFrame(data=all_preds, columns=['head', 'rel', 'tail'])
    df = df.drop_duplicates(keep='first')
    df = df.astype(int)
    return df


# h r t
# def hrt_int_df_2_hrt_anyburl(context_resource: ContextResources, anyburl_dir):
#     df = context_resource.hrt_int_df.copy(deep=True)
#     df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to ent
#     df[['rel']] = df[['rel']].applymap(lambda x: context_resource.id2rel[x])  # to rel
#     df[['head', 'rel', 'tail']].to_csv(anyburl_dir + "all_triples.txt", index=False, header=False, sep='\t')
#     wait_until_file_is_saved(anyburl_dir + "all_triples.txt")
def hrt_int_df_2_hrt_anyburl(context_resource: ContextResources, anyburl_dir):
    df = context_resource.hrt_int_df
    df.to_csv(anyburl_dir + "all_triples.txt", index=False, header=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir + "all_triples.txt")


def split_all_triples_anyburl(context_resource, anyburl_dir, exclude_rels=[]):
    # df = read_hrt_2_df(anyburl_dir + "all_triples.txt")
    df = context_resource.hrt_int_df.copy(deep=True)
    rels = df['rel'].drop_duplicates(keep='first')
    total =len(df.index)
    rate = len(rels.index) * 100 / total
    rate = rate if rate < 0.1 else 0.1
    count_dev = int(total * rate)
    count_dev = len(rels) if count_dev < len(rels) else count_dev
    groups = df.groupby('rel')
    dev_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
    for g in groups:
        r_triples_df = g[1]
        sample_num = int(len(r_triples_df.index) * rate)
        sample_num = 1 if sample_num < 1 else sample_num
        random_sample_count = random.randint(1, sample_num)
        dev_r = r_triples_df.sample(random_sample_count)
        dev_df = pd.concat([dev_df, dev_r])
    if len(dev_df) < count_dev:
        diff_df = pd.concat([df, dev_df, dev_df]).drop_duplicates(keep=False)
        dev_df = pd.concat([dev_df, diff_df.sample(count_dev - len(dev_df))])
    sample_train = pd.concat([df, dev_df, dev_df]).drop_duplicates(keep=False)
    rels_train = sample_train['rel'].drop_duplicates(keep='first')
    if len(rels_train) < len(rels):
        miss_rel = pd.concat([rels, rels_train, rels_train]).drop_duplicates(keep=False)
        filtered_tris = dev_df[dev_df['rel'].isin(list(miss_rel))]
        sample_train = pd.concat([sample_train, filtered_tris])
    sample_train.to_csv(osp.join(anyburl_dir, f'train.txt'), header=False, index=False, sep='\t')
    dev_df.to_csv(osp.join(anyburl_dir, f'valid.txt'), header=False, index=False, sep='\t')
    if len(exclude_rels) > 0:
        df_test = df.query("not rel in @exclude_rels")
    else:
        df_test = df
    df_hr = df_test.drop_duplicates(['head', 'rel'], keep='first')
    df_rt = df_test.drop_duplicates(['rel', 'tail'], keep='first')
    if len(df_hr.index) > len(df_rt.index):
        df_hr = pd.concat([df_hr, df_rt, df_rt]).drop_duplicates(keep=False)
    else:
        df_rt = pd.concat([df_rt, df_hr, df_hr]).drop_duplicates(keep=False)
    df_hr.to_csv(osp.join(anyburl_dir, f'test_hr.txt'), header=False, index=False, sep='\t')
    df_rt.to_csv(osp.join(anyburl_dir, f'test_rt.txt'), header=False, index=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir+'test_hr.txt')
    wait_until_file_is_saved(anyburl_dir+'test_rt.txt')


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
    read_hrt_pred_anyburl_2_hrt_int_df("../outputs/treat/anyburl/predictions/alpha-100", None)
