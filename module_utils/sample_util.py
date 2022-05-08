from __future__ import annotations
from abox_scanner.ContextResources import ContextResources
import pandas as pd
import random
from collections import Counter


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
        tmp_dev_df = tmp_dev_df.reset_index(drop=True)
        sample_left = sample_left.reset_index(drop=True)
        return tmp_dev_df, sample_left

    df_dev, df_train = split_portion(df)
    if produce:
        if len(exclude_rels) > 0:
            df_test = df.query("not rel in @exclude_rels")
            df_test = pd.concat([df_test, df_dev, df_dev]).drop_duplicates(keep="first")
        else:
            df_test = pd.concat([df, df_dev, df_dev]).drop_duplicates(keep="first")
    else:
        df_test, df_train = split_portion(df_train)
    df_train = df_train.reset_index(drop=True)
    df_dev = df_dev.reset_index(drop=True)
    df_test = df_test.reset_index(drop=True)
    return df_train, df_dev, df_test


def split_type_triples(context_resource: ContextResources, top_n_types=50, produce=True):
    ent_num = len(context_resource.entid2classids)
    dev_rate = 0.1
    count_dev = int(ent_num * dev_rate)

    all_classes = [i for cls in context_resource.entid2classids.values() for i in cls]
    top_n = Counter(all_classes).most_common(top_n_types)
    n_types = [i[0] for i in top_n]
    all_ents = pd.concat([context_resource.hrt_int_df['head'], context_resource.hrt_int_df['tail']],
                         axis=0).drop_duplicates(keep='first')
    all_ents = all_ents.values.tolist()

    def split_portion(to_split_list):
        ent_df = pd.DataFrame(data=to_split_list, columns=['ent'])
        sample_dev_ent = ent_df.sample(count_dev, random_state=random.randint(10, 50))
        sample_dev_dict = {ent: [c for c in context_resource.entid2classids[ent] if c in n_types] for ent in sample_dev_ent['ent']}
        sample_remain = {ent: [c for c in context_resource.entid2classids[ent] if c in n_types] for ent in to_split_list if ent not in sample_dev_ent}
        return sample_dev_dict, sample_remain

    sample_dev, sample_train = split_portion(all_ents)
    if produce:
        sample_test = {ent: [c for c in context_resource.entid2classids[ent] if c in n_types] for ent in all_ents}
    else:
        sample_test, sample_train = split_portion(sample_train)
    return sample_train, sample_dev, sample_test




