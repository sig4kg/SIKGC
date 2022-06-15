from __future__ import annotations
from abox_scanner.abox_utils import wait_until_file_is_saved
import os
import os.path as osp
from scripts.run_scripts import mk_dir
from module_utils.sample_util import *


def read_hrts_blp_2_hrt_int_df(hrts_blp_file, context_resource: ContextResources):
    df = pd.read_csv(
        hrts_blp_file, header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.ent2id[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.op2id[x])  # t
    return df[['head', 'rel', 'tail']]


def hrt_int_df_2_hrt_blp(context_resource: ContextResources, hrt_blp_dir, triples_only=False):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to int
    df[['rel']] = df[['rel']].applymap(lambda x: context_resource.id2op[x])  # to int
    df[['head', 'rel', 'tail']].to_csv(hrt_blp_dir + "all_triples.tsv", index=False, header=False, sep='\t')
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


def save_dict_to_file(type_dict, file_name):
    content = ""
    for ent in type_dict:
        content = content + f"{ent}\t" + "\t".join(type_dict[ent]) + "\n"
    with open(file_name, mode='w') as f:
        f.write(content)


def split_data_blp(context_resource: ContextResources, inductive, work_dir, exclude_rels=[]):
    df_rel_train, df_rel_dev, df_rel_test = split_relation_triples(hrt_df=context_resource.hrt_int_df,
                                                                   exclude_rels=exclude_rels,
                                                                   produce=True)
    # if inductive:
    #     drop_entities(work_dir + "all_triples.tsv", train_size=1-rate, valid_size=rate, test_size=0,
    #                   seed=0)
        # os.system(f"cp {work_dir}all_triples.tsv {work_dir}ind-test.tsv")
    # else
    def to_text(tmp_df):
        tmp_df = tmp_df.copy()
        tmp_df['head'] = tmp_df['head'].apply(lambda x: context_resource.id2ent[x])  # to str
        tmp_df['tail'] = tmp_df['tail'].apply(lambda x: context_resource.id2ent[x])  # to str
        tmp_df['rel'] = tmp_df['rel'].apply(lambda x: context_resource.id2op[x])  # to str
        return tmp_df
    # save rel axioms to file
    train_name = "ind-train.tsv" if inductive else "train.tsv"
    dev_name = "ind-dev.tsv" if inductive else "dev.tsv"
    to_text(df_rel_train).to_csv(osp.join(work_dir, train_name), header=False, index=False, sep='\t')
    to_text(df_rel_dev).to_csv(osp.join(work_dir, dev_name), header=False, index=False, sep='\t')
    df_hr = df_rel_test.drop_duplicates(['head', 'rel'], keep='first')
    df_rt = df_rel_test.drop_duplicates(['rel', 'tail'], keep='first')
    if len(df_hr.index) > len(df_rt.index):
        df_hr = pd.concat([df_hr, df_rt, df_rt]).drop_duplicates(keep=False)
    else:
        df_rt = pd.concat([df_rt, df_hr, df_hr]).drop_duplicates(keep=False)
    to_text(df_hr).to_csv(f'{work_dir}test_hr.tsv', header=False, index=False, sep='\t')
    to_text(df_rt).to_csv(f'{work_dir}test_rt.tsv', header=False, index=False, sep='\t')
    wait_until_file_is_saved(f'{work_dir}test_hr.tsv')
    wait_until_file_is_saved(f'{work_dir}test_rt.tsv')


def generate_silver_rel_eval_file(context_resource: ContextResources, work_dir):
    tmp_df = context_resource.silver_rel.copy(deep=True)
    tmp_df[['head', 'tail']] = tmp_df[['head', 'tail']].applymap(lambda x: context_resource.id2ent[x])  # to str
    tmp_df['rel'] = tmp_df['rel'].apply(lambda x: context_resource.id2op[x])  # to str
    tmp_df.to_csv(f'{work_dir}test_rel_silver.tsv', header=False, index=False, sep='\t')
    wait_until_file_is_saved(f'{work_dir}test_rel_silver.tsv')


def prepare_blp(source_dir, work_dir):
    mk_dir(work_dir)
    os.system(f"[ -f {source_dir}entity2text.txt ] && cp {source_dir}entity2text.txt {work_dir}entity2text.txt")
    os.system(f"[ -f {source_dir}relation2text.txt ] && cp {source_dir}relation2text.txt {work_dir}relation2text.txt")
    os.system(f"[ -f {source_dir}entity2type.txt ] && cp {source_dir}entity2type.txt {work_dir}entity2type.txt")
    os.system(f"[ -f {source_dir}entity2textlong.txt ] && cp {source_dir}entity2textlong.txt {work_dir}entity2textlong.txt")
    os.system(f"[ -f {source_dir}invalid_hrt.txt ] && cp {source_dir}invalid_hrt.txt {work_dir}invalid_hrt.txt")


def clean_blp(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('echo ../scripts/clean_blp.sh')
    os.system('../scripts/clean_blp.sh ' + work_dir)


def wait_until_blp_data_ready(work_dir, inductive=False):
    if inductive:
        # wait_until_file_is_saved(work_dir + "dev-ents.txt")
        # wait_until_file_is_saved(work_dir + "test-ents.txt")
        # wait_until_file_is_saved(work_dir + "train-ents.txt")
        wait_until_file_is_saved(work_dir + "ind-dev.tsv")
        wait_until_file_is_saved(work_dir + "ind-test.tsv")
        wait_until_file_is_saved(work_dir + "ind-train.tsv")
    else:
        wait_until_file_is_saved(work_dir + "dev.tsv")
        wait_until_file_is_saved(work_dir + "train.tsv")