from __future__ import annotations
from abox_scanner.ContextResources import ContextResources
from abox_scanner.abox_utils import wait_until_file_is_saved, save_to_file
import os
import os.path as osp
from itertools import zip_longest
import pandas as pd
import random
# train, dev, tests


def split_relation_triples(context_resource: ContextResources, exclude_rels=[], produce=True):
    df = context_resource.hrt_int_df.copy(deep=True)
    rels = df['rel'].drop_duplicates(keep='first')
    total = len(df.index)
    dev_rate = len(rels.index) * 100 / total
    dev_rate = dev_rate if dev_rate < 0.1 else 0.1
    count_dev = int(total * dev_rate)
    count_dev = len(rels) if count_dev < len(rels) else count_dev

    def split_portion(to_split: pd.DataFrame):
        groups = to_split.groupby('rel')
        tmp_dev_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        for g in groups:
            r_triples_df = g[1]
            sample_num = int(len(r_triples_df.index) * dev_rate)
            sample_num = 1 if sample_num < 1 else sample_num
            random_sample_count = random.randint(1, sample_num)
            dev_r = r_triples_df.sample(random_sample_count)
            tmp_dev_df = pd.concat([tmp_dev_df, dev_r])
        if len(tmp_dev_df) < count_dev:
            diff_df = pd.concat([df, tmp_dev_df, tmp_dev_df]).drop_duplicates(keep=False)
            tmp_dev_df = pd.concat([tmp_dev_df, diff_df.sample(count_dev - len(tmp_dev_df))])
        sample_left = pd.concat([df, tmp_dev_df, tmp_dev_df]).drop_duplicates(keep=False)
        rels_train_left = sample_left['rel'].drop_duplicates(keep='first')
        if len(rels_train_left) < len(rels):
            miss_rel = pd.concat([rels, rels_train_left, rels_train_left]).drop_duplicates(keep=False)
            filtered_tris = tmp_dev_df[tmp_dev_df['rel'].isin(list(miss_rel))]
            sample_left = pd.concat([sample_left, filtered_tris])
        return tmp_dev_df, sample_left

    df_dev, df_train = split_portion(df)
    if produce:
        if len(exclude_rels) > 0:
            df_test = df.query("not rel in @exclude_rels")
        else:
            df_test = df
    else:
        df_test, df_train = split_portion(df_train)
    return df_train, df_dev, df_test


def split_type_triples(context_resource: ContextResources, exclude_ents=[], produce=True):
    type_hrt = context_resource.type2hrt_int_df()
    ent_num = len(context_resource.entid2classids)
    dev_rate = 0.1
    count_dev = int(ent_num * dev_rate)

    def split_portion(to_split_hrt: pd.DataFrame):
        ent_df = to_split_hrt[['head']].drop_duplicates(keep='first')
        sample_dev_ent = ent_df.sample(count_dev)
        sample_dev_hrt = to_split_hrt.query("head in @sample_dev_ent")
        sample_remain = pd.concat([to_split_hrt, sample_dev_hrt, sample_dev_hrt]).drop_duplicates(keep=False)
        return sample_dev_hrt, sample_remain

    df_dev, df_train = split_portion(type_hrt)
    if produce:
        if len(exclude_ents) > 0:
            df_test = type_hrt.query("not rel in @exclude_ents")
        else:
            df_test = type_hrt
    else:
        df_test, df_train = split_portion(df_train)
    return df_train, df_dev, df_test




