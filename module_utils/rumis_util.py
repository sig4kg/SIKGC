from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df


def read_hrt_rumis_2_hrt_int_df(hrt_rumis_file, context_resource: ContextResources):
    df = pd.read_csv(
        hrt_rumis_file, header=None, names=['head', 'rel', 'tail'], sep="\t")
    df = df.apply(lambda x: x.str[1:-1])
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.ent2id[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.rel2id[x])  # to int
    return df


def read_hrt_original_2_hrt_rumis(hrt_original, hrt_rumis_file):
    df = read_hrt_2_df(hrt_original)
    df = df.apply(lambda x: '<' + x + '>')
    df[['head', 'rel', 'tail']].to_csv(hrt_rumis_file, header=None, index=None, sep='\t')


def hrt_int_df_2_hrt_rumis(context_resource: ContextResources, hrt_rumis_file):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: '<' + context_resource.id2ent[x] + '>')
    df[['rel']] = df[['rel']].applymap(lambda x: '<' + context_resource.id2rel[x] + '>')  # to int
    df[['head', 'rel', 'tail']].to_csv(hrt_rumis_file, header=None, index=None, sep='\t')
