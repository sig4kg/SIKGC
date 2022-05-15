from __future__ import annotations
import os
import pandas as pd
from abox_scanner.ContextResources import ContextResources
from module_utils.file_util import wait_until_file_is_saved


def read_hrt_rumis_2_hrt_int_df(hrt_rumis_file, context_resource: ContextResources):
    df = pd.read_csv(
        hrt_rumis_file, header=None, names=['head', 'rel', 'tail'], sep="\t")
    df = df.apply(lambda x: x.str[1:-1])
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.ent2id[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.op2id[x])  # to int
    return df


def hrt_int_df_2_hrt_rumis(context_resource: ContextResources, hrt_rumis_file):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: '<' + context_resource.id2ent[x] + '>')
    df[['rel']] = df[['rel']].applymap(lambda x: '<' + context_resource.id2op[x] + '>')  # to int
    df[['head', 'rel', 'tail']].to_csv(hrt_rumis_file, header=None, index=None, sep='\t')


def run_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/run_rumis.sh ' + work_dir)
    wait_until_file_is_saved(work_dir + "/ideal.data.txt", 60)
    wait_until_file_is_saved(work_dir + "/dlv.bin", 10)
    wait_until_file_is_saved(work_dir + "/rumis-1.0.jar", 10)


def clean_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_rumis.sh ' + work_dir)

