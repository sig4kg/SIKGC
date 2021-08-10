from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df
from blp.blp_data_utils import drop_entities

def read_hrts_blp_2_hrt_int_df(hrts_blp_file, context_resource: ContextResources):
    df = pd.read_csv(
        hrts_blp_file, header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.ent2id[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.rel2id[x])  # t
    return df[['head', 'rel', 'tail']]


def hrt_int_df_2_hrt_blp(context_resource: ContextResources, hrt_blp_dir):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.id2rel[x])  # to int
    df[['head', 'rel', 'tail']].to_csv(hrt_blp_dir + "all_triples.tsv", index=False, header=False, sep='\t')
    entities = pd.DataFrame(data=context_resource.ent2id.keys())
    rels = pd.DataFrame(data=context_resource.rel2id.keys())
    entities.to_csv(hrt_blp_dir + 'entities.txt', index=False, header=False)
    rels.to_csv(hrt_blp_dir + 'relations.txt', index=False, header=False)
    # drop_entities(hrt_blp_dir + "all_triples.tsv", train_size=0.9, valid_size=0.1, test_size=0, types_file=hrt_blp_dir+"top50-entity2type.txt")


def wait_until_blp_data_ready(hrt_blp_dir):
    pass