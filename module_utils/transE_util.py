from __future__ import annotations
import pandas as pd
from abox_scanner.abox_utils import wait_until_file_is_saved, ContextResources
import os

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


# def hrt_df_2_htr_transE(hrt_df, transE_train_file):
#     count = len(hrt_df)
#     first_line_df = pd.DataFrame(data=[[count, '', '']], columns=['head', 'rel', 'tail'])
#     df2 = pd.concat([first_line_df, hrt_df], 0)
#     df2[['head', 'tail', 'rel']].to_csv(transE_train_file, header=None, index=None, sep='\t')


# def read_hrt_2_htr_transE(hrt_triples_file, transE_train_file):
#     df = pd.read_csv(
#         hrt_triples_file, header=None, names=['head', 'rel', 'tail'], sep='\t')
#     hrt_df_2_htr_transE(df, transE_train_file)


def context_2_hrt_transE(work_dir, context_resources: ContextResources, exclude_rels=[]):
    count = len(context_resources.hrt_int_df)
    first_line_df = pd.DataFrame(data=[[count, '', '']], columns=['head', 'rel', 'tail'])
    df2_train = pd.concat([first_line_df, context_resources.hrt_int_df], 0)
    df2_train[['head', 'tail', 'rel']].to_csv(work_dir + "train/train2id.txt", header=False, index=False, sep='\t')
    wait_until_file_is_saved(work_dir + "train/train2id.txt", 60)
    if len(exclude_rels) > 0:
        excludes = [context_resources.rel2id[i] for i in exclude_rels if i in context_resources.rel2id]
        df_test = context_resources.hrt_int_df.query("not rel in @excludes")
        count_line = pd.DataFrame(data=[[len(df_test.index), '', '']], columns=['head', 'rel', 'tail'])
        df_test = pd.concat([count_line, df_test], 0)
        df_test[['head', 'tail', 'rel']].to_csv(f"{work_dir}train/test2id.txt", header=False, index=False, sep='\t')
    else:
        os.system(f"cp {work_dir}train/train2id.txt {work_dir}train/test2id.txt")
    wait_until_file_is_saved(work_dir + "train/test2id.txt", 60)
    os.system(f"cp {work_dir}train/train2id.txt {work_dir}train/valid2id.txt")


def wait_until_train_pred_data_ready(work_dir):
    os.system(f"[ -f {work_dir}type_constrain.txt ] && cp {work_dir}type_constrain.txt {work_dir}train/")
    wait_until_file_is_saved(work_dir + "train/valid2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/type_constrain.txt", 60)
    wait_until_file_is_saved(work_dir + "train/entity2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/relation2id.txt", 60)
    wait_until_file_is_saved(work_dir + "train/train2id.txt", 60)
