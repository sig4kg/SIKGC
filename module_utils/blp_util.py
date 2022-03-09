from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df
from blp.blp_data_utils import drop_entities
from abox_scanner.abox_utils import wait_until_file_is_saved
import os
import os.path as osp
from scripts.run_scripts import mk_dir
import csv


def read_hrts_blp_2_hrt_int_df(hrts_blp_file, context_resource: ContextResources):
    df = pd.read_csv(
        hrts_blp_file, header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.ent2id[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.rel2id[x])  # t
    return df[['head', 'rel', 'tail']]


def hrt_int_df_2_hrt_blp(context_resource: ContextResources, hrt_blp_dir, triples_only=False):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.id2rel[x])  # to int
    df[['head', 'rel', 'tail']].to_csv(hrt_blp_dir + "all_triples.tsv", index=False, header=False, sep='\t')
    # pandas has issue with quotes, alternatively write to file
    # entities = pd.DataFrame(data=context_resource.ent2id.keys())
    # rels = pd.DataFrame(data=context_resource.rel2id.keys())
    # entities.to_csv(hrt_blp_dir + 'entities.txt', index=False, header=False)
    # rels.to_csv(hrt_blp_dir + 'relations.txt', index=False, header=False)
    if not triples_only:
        all_valid_entities = pd.concat([df['head'], df['tail']]).drop_duplicates(keep='first')
        all_valid_rels = df['rel'].drop_duplicates(keep='first')
        with open(hrt_blp_dir + "entities.txt", encoding='utf-8', mode='w') as out_f:
            for item in list(all_valid_entities):
                out_f.write(item + '\n')
            out_f.close()
        with open(hrt_blp_dir + "relations.txt", encoding='utf-8', mode='w') as out_f:
            for item in list(all_valid_rels):
                out_f.write(item + '\n')
            out_f.close()


def split_all_triples(context_resource, work_dir, inductive=False, exclude_rels=[]):
    df = read_hrt_2_df(work_dir + "all_triples.tsv")
    rels = df['rel'].drop_duplicates(keep='first')
    total =len(df.index)
    rate = len(rels.index) * 50 / total
    rate = rate if rate < 0.1 else 0.1
    if inductive:
        drop_entities(work_dir + "all_triples.tsv", train_size=1-rate, valid_size=rate, test_size=0,
                      seed=0)
        # os.system(f"cp {work_dir}all_triples.tsv {work_dir}ind-test.tsv")
    else:
        count_dev = int(total * rate)
        count_dev = len(rels) if count_dev < len(rels) else count_dev
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
        sample_train.to_csv(osp.join(work_dir, f'train.tsv'), header=False, index=False, sep='\t')
        sample_dev.to_csv(osp.join(work_dir, f'dev.tsv'), header=False, index=False, sep='\t')
        # if len(exclude_rels) > 0:
        #     df_test = df.query("not rel in @exclude_rels")
        #     df_test.to_csv(f"{work_dir}test.tsv", header=False, index=False, sep='\t')
        # else:
        #     os.system(f"cp {work_dir}all_triples.tsv {work_dir}test.tsv")
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
    df_hr.to_csv(f'{work_dir}test_hr.tsv', header=False, index=False, sep='\t')
    df_rt.to_csv(f'{work_dir}test_rt.tsv', header=False, index=False, sep='\t')
    wait_until_file_is_saved(f'{work_dir}test_hr.tsv')
    wait_until_file_is_saved(f'{work_dir}test_rt.tsv')


def prepare_blp(source_dir, work_dir):
    mk_dir(work_dir)
    os.system(f"[ -f {source_dir}entity2text.txt ] && cp {source_dir}entity2text.txt {work_dir}entity2text.txt")
    os.system(f"[ -f {source_dir}relation2text.txt ] && cp {source_dir}relation2text.txt {work_dir}relation2text.txt")
    os.system(f"[ -f {source_dir}entity2type.txt ] && cp {source_dir}entity2type.txt {work_dir}entity2type.txt")
    os.system(f"[ -f {source_dir}entity2textlong.txt ] && cp {source_dir}entity2textlong.txt {work_dir}entity2textlong.txt")


def wait_until_blp_data_ready(work_dir, inductive=False):
    if inductive:
        wait_until_file_is_saved(work_dir + "dev-ents.txt")
        wait_until_file_is_saved(work_dir + "test-ents.txt")
        wait_until_file_is_saved(work_dir + "train-ents.txt")
        wait_until_file_is_saved(work_dir + "ind-dev.tsv")
        wait_until_file_is_saved(work_dir + "ind-test.tsv")
        wait_until_file_is_saved(work_dir + "ind-train.tsv")
    else:
        wait_until_file_is_saved(work_dir + "dev.tsv")
        wait_until_file_is_saved(work_dir + "train.tsv")