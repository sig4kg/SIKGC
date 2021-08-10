from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import wait_until_file_is_saved, ContextResources


def read_hrts_2_hrt_df(hrts_file):
    df = pd.read_csv(
        hrts_file, header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    return df[['head', 'rel', 'tail']]


def read_htr_transE_2_hrt_df(htr_with_count_file):
    df = pd.read_csv(
        htr_with_count_file, header=None, names=['head', 'tail', 'rel'], dtype={'head':str, 'tail':str, 'rel':str}, sep="\t")
    count = int(df.loc[0, 'head'])
    df = df.iloc[1:]
    df.astype(int)
    return count, df


def hrt_df_2_htr_transE(hrt_df, transE_train_file):
    count = len(hrt_df)
    first_line_df = pd.DataFrame(data=[[count, '', '']], columns=['head', 'rel', 'tail'])
    df2 = pd.concat([first_line_df, hrt_df], 0)
    df2[['head', 'tail', 'rel']].to_csv(transE_train_file, header=None, index=None, sep='\t')


def read_hrt_2_htr_transE(hrt_triples_file, transE_train_file):
    df = pd.read_csv(
        hrt_triples_file, header=None, names=['head', 'rel', 'tail'], sep='\t')
    hrt_df_2_htr_transE(df, transE_train_file)


def context_2_hrt_transE(work_dir, context_resources: ContextResources):
    hrt_df_2_htr_transE(context_resources.hrt_int_df, work_dir + "train/train2id.txt")


def wait_until_train_pred_data_ready(work_dir):
    wait_until_file_is_saved(work_dir + "train/valid2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/type_constrain.txt", 60)
    wait_until_file_is_saved(work_dir + "train/entity2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/relation2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/train2id.txt", 60)
