from pykeen.datasets import Nations
from pykeen.datasets.conceptnet import ConceptNet
import argparse
from tqdm import tqdm
from file_util import init_dir
from log_util import get_file_logger
from pipelines.exp_config import *
from pipeline_util import *
from pipelines.ProducerBlock import PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from blp.producer import ex
import torch


def format_dataset(workdir):
    dataset = ConceptNet()
    # dataset = Nations()
    train_and_test = torch.concat([dataset.training.mapped_triples, dataset.testing.mapped_triples], 0)
    dev = dataset.validation.mapped_triples
    all_triples = torch.concat([train_and_test, dev], 0)
    df = pd.DataFrame(all_triples.numpy(), columns=['head', 'rel', 'tail'])
    df_train = pd.DataFrame(train_and_test.numpy(), columns=['head', 'rel', 'tail'])
    df_dev = pd.DataFrame(dev.numpy(), columns=['head', 'rel', 'tail'])
    df.to_csv(workdir + "all_triples.tsv", index=False, header=False, sep='\t')
    df_train.to_csv(workdir + "train.tsv", index=False, header=False, sep='\t')
    df_dev.to_csv(workdir + "dev.tsv", index=False, header=False, sep='\t')
    df_hr = df_train.drop_duplicates(['head', 'rel'], keep='first')
    df_rt = df_train.drop_duplicates(['rel', 'tail'], keep='first')
    if len(df_hr.index) > len(df_rt.index):
        df_hr = pd.concat([df_hr, df_rt, df_rt]).drop_duplicates(keep=False)
    else:
        df_rt = pd.concat([df_rt, df_hr, df_hr]).drop_duplicates(keep=False)
    df_hr.to_csv(f'{workdir}test_hr.tsv', header=False, index=False, sep='\t')
    df_rt.to_csv(f'{workdir}test_rt.tsv', header=False, index=False, sep='\t')
    all_valid_entities = pd.concat([df['head'], df['tail']]).drop_duplicates(keep='first')
    all_valid_rels = df['rel'].drop_duplicates(keep='first')
    with open(workdir + "entities.txt", encoding='utf-8', mode='w') as out_f:
        for item in list(all_valid_entities):
            out_f.write(str(item) + '\n')
        out_f.close()
    with open(workdir + "relations.txt", encoding='utf-8', mode='w') as out_f:
        for item in list(all_valid_rels):
            out_f.write(str(item) + '\n')
        out_f.close()
    return df_train


def read_hrt_2_df(work_dir):
    df = pd.read_csv(
        work_dir + "blp_new_triples.csv", header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    return df[['head', 'rel', 'tail']]


def run_E_method_without_ACC(work_dir, model, loop=2):
    init_dir(work_dir)
    blp_conf = BLPConfig().get_blp_config(rel_model=model,
                                          inductive=False,
                                          dataset='Other',
                                          schema_aware=False,
                                          silver_eval=False,
                                          do_produce=True)
    blp_conf.update({'work_dir': work_dir})
    # train.tsv, dev.tsv
    train_df = format_dataset(work_dir)
    for l in tqdm(range(loop)):
        wait_until_blp_data_ready(work_dir, inductive=False)
        # 1. run blp
        ex.run(config_updates=blp_conf)
        wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)
        pred_hrt_df = read_hrt_2_df(work_dir).drop_duplicates(
            keep='first').reset_index(drop=True)
        print("all produced triples: " + str(len(pred_hrt_df.index)))

        logger = get_file_logger(file_name='test.log')
        new_hrt_df = pd.concat([pred_hrt_df, train_df, train_df]).drop_duplicates(
            keep=False)

        new_count = len(new_hrt_df.index)
        if new_count == 0:
            logger.info(f"new_count: 0")
            return
        # 3. update train set
        expanded_df = pd.concat([train_df, pred_hrt_df]).drop_duplicates(keep="first").\
            reset_index(drop=True)
        train_df = expanded_df
        expanded_df.to_csv(work_dir + "train.tsv", index=False, header=False, sep='\t')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    parser.add_argument('--model', type=str, default="complex")
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--loop', type=int, default=2)
    argss = parser.parse_args()
    run_E_method_without_ACC(argss.work_dir, argss.model, loop=argss.loop)