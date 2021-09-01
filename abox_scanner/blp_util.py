from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df
from blp.blp_data_utils import drop_entities
from abox_scanner.abox_utils import wait_until_file_is_saved
import os
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
        with open(hrt_blp_dir + "entities.txt", encoding='utf-8', mode='w') as out_f:
            for item in context_resource.ent2id.keys():
                out_f.write(item + '\n')
            out_f.close()
        with open(hrt_blp_dir + "relations.txt", encoding='utf-8', mode='w') as out_f:
            for item in context_resource.rel2id.keys():
                out_f.write(item + '\n')
            out_f.close()

def split_all_triples(work_dir, inductive=False):
    if inductive:
        drop_entities(work_dir + "all_triples.tsv", train_size=0.9, valid_size=0.1, test_size=0.0,
                      seed=0)
        os.system(f"cp {work_dir}all_triples.tsv {work_dir}ind-test.tsv")
    else:
        os.system(f"shuf {work_dir}all_triples.tsv | split -a1 -l $(( $(wc -l <{work_dir}all_triples.tsv) * 80 / 100 )) - {work_dir}part")
        os.system(f"mv {work_dir}parta {work_dir}train.tsv")
        os.system(f"mv {work_dir}partb {work_dir}dev.tsv")
        os.system(f"cp {work_dir}all_triples.tsv {work_dir}test.tsv")



def prepare_blp(source_dir, work_dir):
    os.system(f"cp {source_dir}entity2text.txt {work_dir}entity2text.txt")
    os.system(f"cp {source_dir}relation2text.txt {work_dir}relation2text.txt")
    os.system(f"cp {source_dir}entity2type.txt {work_dir}entity2type.txt")
    os.system(f"cp {source_dir}entity2textlong.txt {work_dir}entity2textlong.txt")


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