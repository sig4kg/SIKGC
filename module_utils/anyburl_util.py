from __future__ import annotations
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df
from abox_scanner.abox_utils import wait_until_file_is_saved, save_file
import os
import os.path as osp
from itertools import zip_longest
import pandas as pd


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

            tmp_preds = [[context_resource.ent2id[i[0]],
                          context_resource.rel2id[i[1]],
                          context_resource.ent2id[i[2]]] for i in tmp_preds]
            all_preds.extend(tmp_preds)
    df = pd.DataFrame(data=all_preds, columns=['head', 'rel', 'tail'])
    df = df.drop_duplicates(keep='first')
    return df


# h r t
def hrt_int_df_2_hrt_anyburl(context_resource: ContextResources, anyburl_dir):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to ent
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.id2rel[x])  # to rel
    df[['head', 'rel', 'tail']].to_csv(anyburl_dir + "all_triples.txt", index=False, header=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir + "all_triples.txt")


def split_all_triples_anyburl(anyburl_dir):
    df = read_hrt_2_df(anyburl_dir + "all_triples.txt")
    rels = df['rel'].drop_duplicates(keep='first')
    count_dev = int(len(df) * 0.1 if len(rels) < len(df) * 0.1 else len(rels))
    sample_dev = df.groupby('rel').sample(n=1)
    if len(sample_dev) < count_dev:
        diff_df = pd.concat([df, sample_dev, sample_dev]).drop_duplicates(keep=False)
        sample_dev = pd.concat([sample_dev, diff_df.sample(count_dev - len(sample_dev))])
    sample_train = pd.concat([df, sample_dev, sample_dev]).drop_duplicates(keep=False)
    rels_train = sample_train['rel'].drop_duplicates(keep='first')
    if len(rels_train) < len(rels):
        miss_rel = pd.concat([rels, rels_train, rels_train]).drop_duplicates(keep=False)
        filtered_tris = sample_dev[sample_dev['rel'].isin(list(miss_rel))]
        sample_train = pd.concat([sample_train, filtered_tris])
    sample_train.to_csv(osp.join(anyburl_dir, f'train.txt'), header=False, index=False, sep='\t')
    sample_dev.to_csv(osp.join(anyburl_dir, f'valid.txt'), header=False, index=False, sep='\t')
    os.system(f"cp {anyburl_dir}all_triples.txt {anyburl_dir}test.txt")


def prepare_anyburl_configs(anyburl_dir):
    config_apply = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_TEST      = {anyburl_dir}test.txt\n" \
                   f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                   f"PATH_RULES     = {anyburl_dir}rules/alpha-100\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}predictions/alpha-100\n" \
                   "UNSEEN_NEGATIVE_EXAMPLES = 5\n" \
                   "TOP_K_OUTPUT = 10\n"\
                   "WORKER_THREADS = 7"
    config_eval = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                  f"PATH_TEST      = {anyburl_dir}test.txt\n" \
                  f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                  f"PATH_PREDICTIONS   = {anyburl_dir}predictions/alpha-100"
    config_learn = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}rules/alpha\n" \
                   f"SNAPSHOTS_AT = 100\n" \
                   f"WORKER_THREADS = 4\n"
    save_file(config_apply, anyburl_dir + "config-apply.properties")
    save_file(config_eval, anyburl_dir + "config-eval.properties")
    save_file(config_learn, anyburl_dir + "config-learn.properties")


def wait_until_anyburl_data_ready(anyburl_dir):
    wait_until_file_is_saved(anyburl_dir + "dev.txt")
    wait_until_file_is_saved(anyburl_dir + "train.txt")
    wait_until_file_is_saved(anyburl_dir + "test.txt")
    wait_until_file_is_saved(anyburl_dir + "config-apply.properties")
    wait_until_file_is_saved(anyburl_dir + "config-eval.properties")
    wait_until_file_is_saved(anyburl_dir + "config-learn.properties")


if __name__ == "__main__":
    read_hrt_pred_anyburl_2_hrt_int_df("../outputs/treat/anyburl/predictions/alpha-100", None)
