from __future__ import annotations
from sklearn.metrics import precision_recall_fscore_support
from abox_scanner.abox_utils import wait_until_file_is_saved, save_to_file
import os
import os.path as osp
from itertools import zip_longest
import numpy as np
from sklearn import metrics
from sklearn.preprocessing import MultiLabelBinarizer
from module_utils.file_util import init_dir
from module_utils.sample_util import *


def read_hrt_pred_anyburl_2_hrt_int_df(pred_anyburl_file, pred_tail_only=False) -> pd.DataFrame:
    with open(pred_anyburl_file) as f:
        lines = f.readlines()
        chunks = zip_longest(*[iter(lines)] * 3, fillvalue='')
        all_preds = []
        for chunk in chunks:
            tmp_preds = []
            original_triple = chunk[0].strip().split()
            h = original_triple[0]
            r = original_triple[1]
            t = original_triple[2]
            pred_t = chunk[2][7:].strip().split('\t')
            pred_ts = zip_longest(*[iter(pred_t)] * 2, fillvalue='')  # preds and scores
            tmp_preds.extend([[h, r, pt[0]] for pt in pred_ts if pt[0] != ''])
            if not pred_tail_only:
                pred_h = chunk[1][7:].strip().split('\t')
                pred_hs = zip_longest(*[iter(pred_h)] * 2, fillvalue='')  # preds and scores
                tmp_preds.extend([[ph[0], r, t] for ph in pred_hs if ph[0] != ''])
            all_preds.extend(tmp_preds)
    df = pd.DataFrame(data=all_preds, columns=['head', 'rel', 'tail'])
    df = df.drop_duplicates(keep='first')
    df = df.astype(int)
    return df


def read_type_pred_and_scores(pred_anyburl_file, all_classes) -> dict:
    all_preds = dict()
    with open(pred_anyburl_file) as f:
        lines = f.readlines()
        chunks = zip_longest(*[iter(lines)] * 3, fillvalue='')
        for chunk in chunks:
            tmp_preds = []
            original_triple = chunk[0].strip().split()
            h = original_triple[0]
            pred_t = chunk[2][7:].strip().split('\t')
            pred_ts = zip_longest(*[iter(pred_t)] * 2, fillvalue='')  # preds and scores
            tmp_preds.extend([(int(pt[0]), float(pt[1])) for pt in pred_ts if pt[0] != '' and int(pt[0]) in all_classes])
            all_preds.update({int(h): tmp_preds})
    return all_preds


def get_optimal_threshold(pred_anyburl_file, ground_truth_dict, all_classes):
    pred_dict = read_type_pred_and_scores(pred_anyburl_file, all_classes)
    ents = pred_dict.keys()
    threshold = np.arange(0.05, 0.4, 0.02)
    mlb = MultiLabelBinarizer()
    num = len(ents)
    scores = []  # Store the list of f1 scores for prediction on each threshold
    for thresh in threshold:
        y = [[cs[0] for cs in pred_dict[e] if cs[1] >= thresh] for e in ents]
        for e in ents:
            y.append(ground_truth_dict[e])
        yt = mlb.fit_transform(y)
        y_true = yt[num:]
        y_pred = yt[:num]
        y_true = np.array(y_true).ravel()
        y_pred = np.array(y_pred).ravel()
        scores.append(metrics.f1_score(y_true, y_pred, average='macro'))
    # find the optimal threshold
    opt_thresh = threshold[scores.index(max(scores))]
    log_str = "-------blp type prediction eval---------\n" + \
              f'Type prediction: Optimal Threshold Value = {opt_thresh}\n'
    print(log_str)
    return opt_thresh


def get_silver_type_scores(pred_anyburl_file, ground_truth_dict, threshhold, all_classes):
    pred_dict = read_type_pred_and_scores(pred_anyburl_file, all_classes)
    ents = pred_dict.keys()
    mlb = MultiLabelBinarizer()
    num = len(ents)
    y = [[cs[0] for cs in pred_dict[e] if cs[1] >= threshhold] for e in ents]
    for e in ents:
        y.append(ground_truth_dict[e])
    yt = mlb.fit_transform(y)
    y_true = yt[num:]
    y_pred = yt[:num]
    y_true = np.array(y_true).ravel()
    y_pred = np.array(y_pred).ravel()
    scores = metrics.classification_report(y_true, y_pred)
    return scores


def read_type_pred_to_df(pred_anyburl_file, all_classes, threshhold):
    pred_dict = read_type_pred_and_scores(pred_anyburl_file, all_classes)
    ents = pred_dict.keys()
    pred_types = {e: [cs[0] for cs in pred_dict[e] if cs[1] >= threshhold] for e in ents}
    return type2hrt_int_df(pred_types)


def type2hrt_int_df(type_dict) -> pd.DataFrame:
    type_hrt = []
    for entid in type_dict:
        h = entid
        r = 0
        typeOfe = type_dict[entid]
        ent_type_hrt = [[h, r, t] for t in typeOfe]
        type_hrt.extend(ent_type_hrt)
    type_df = pd.DataFrame(data=type_hrt, columns=['head', 'rel', 'tail'])
    return type_df


def split_all_triples_anyburl(context_resource: ContextResources, anyburl_dir, exclude_rels=[], produce=True):
    df_rel_train, df_rel_dev, df_rel_test = split_relation_triples(hrt_df=context_resource.hrt_int_df,
                                                                   exclude_rels=exclude_rels,
                                                                   produce=produce)
    dict_type_train, dict_type_dev, dict_type_test = split_type_triples(context_resource=context_resource,
                                                                        top_n_types=50,
                                                                        produce=produce)
    df_type_train = type2hrt_int_df(dict_type_train)
    df_type_dev = type2hrt_int_df(dict_type_dev)
    df_train = pd.concat([df_rel_train, df_type_train]).reset_index(drop=True)
    df_dev = pd.concat([df_rel_dev, df_type_dev]).reset_index(drop=True)
    df_train.to_csv(osp.join(anyburl_dir, f'train.txt'), header=False, index=False, sep='\t')
    df_dev.to_csv(osp.join(anyburl_dir, f'valid.txt'), header=False, index=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir + 'train.txt')
    wait_until_file_is_saved(anyburl_dir + 'valid.txt')
    if produce:
        df_hr = df_rel_test.drop_duplicates(['head', 'rel'], keep='first')
        df_rt = df_rel_test.drop_duplicates(['rel', 'tail'], keep='first')
        if len(df_hr.index) > len(df_rt.index):
            df_hr = pd.concat([df_hr, df_rt, df_rt]).drop_duplicates(keep=False)
        else:
            df_rt = pd.concat([df_rt, df_hr, df_hr]).drop_duplicates(keep=False)
        df_hr.to_csv(osp.join(anyburl_dir, f'test_hr.txt'), header=False, index=False, sep='\t')
        df_rt.to_csv(osp.join(anyburl_dir, f'test_rt.txt'), header=False, index=False, sep='\t')
        df_test_type = type2hrt_int_df(dict_type_test).drop_duplicates(['head'], keep='first')
        df_test_type.to_csv(osp.join(anyburl_dir, f'test_type.txt'), header=False, index=False, sep='\t')
        wait_until_file_is_saved(anyburl_dir + 'test_hr.txt')
        wait_until_file_is_saved(anyburl_dir + 'test_rt.txt')
        wait_until_file_is_saved(anyburl_dir + 'test_type.txt')


def generate_silver_eval_file(context_resource: ContextResources, anyburl_dir):
    df_type_test = type2hrt_int_df(context_resource.silver_type)
    df_type_test.to_csv(osp.join(anyburl_dir, f'test_type_silver.txt'), header=False, index=False, sep='\t')
    context_resource.silver_rel.to_csv(osp.join(anyburl_dir, f'test_rel_silver.txt'), header=False, index=False, sep='\t')
    wait_until_file_is_saved(anyburl_dir + 'test_type_silver.txt')
    wait_until_file_is_saved(anyburl_dir + 'test_rel_silver.txt')


def prepare_anyburl_configs(anyburl_dir, pred_with='hr'):
    config_apply = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_TEST      = {anyburl_dir}test_{pred_with}.txt\n" \
                   f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                   f"PATH_RULES     = {anyburl_dir}rules/alpha-100\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}predictions/alpha-100\n" \
                   "UNSEEN_NEGATIVE_EXAMPLES = 5\n" \
                   "TOP_K_OUTPUT = 10\n" \
                   "WORKER_THREADS = 7"
    config_eval = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                  f"PATH_TEST      = {anyburl_dir}test_{pred_with}.txt\n" \
                  f"PATH_VALID     = {anyburl_dir}valid.txt\n" \
                  f"PATH_PREDICTIONS   = {anyburl_dir}predictions/alpha-100"
    config_learn = f"PATH_TRAINING  = {anyburl_dir}train.txt\n" \
                   f"PATH_OUTPUT    = {anyburl_dir}rules/alpha\n" \
                   f"SNAPSHOTS_AT = 100\n" \
                   f"WORKER_THREADS = 4\n"
    save_to_file(config_apply, anyburl_dir + "config-apply.properties")
    save_to_file(config_eval, anyburl_dir + "config-eval.properties")
    save_to_file(config_learn, anyburl_dir + "config-learn.properties")
    wait_until_file_is_saved(anyburl_dir + "config-apply.properties")
    wait_until_file_is_saved(anyburl_dir + "config-eval.properties")
    wait_until_file_is_saved(anyburl_dir + "config-learn.properties")


def clean_anyburl_tmp_files(anyburl_dir):
    init_dir(f"{anyburl_dir}last_round/")
    os.system(f"[ -f {anyburl_dir}predictions/alpha* ] && mv {anyburl_dir}predictions/* {anyburl_dir}last_round/")
    os.system(f"[ -f {anyburl_dir}config-apply.properties ] && mv {anyburl_dir}config-apply.properties {anyburl_dir}last_round/")
    os.system(f"[ -f {anyburl_dir}anyburl_eval.log ] && rm {anyburl_dir}anyburl_eval.log")



def wait_until_anyburl_data_ready(anyburl_dir):
    wait_until_file_is_saved(anyburl_dir + "test_hr.txt")
    wait_until_file_is_saved(anyburl_dir + "test_rt.txt")
    wait_until_file_is_saved(anyburl_dir + "valid.txt")
    wait_until_file_is_saved(anyburl_dir + "train.txt")


def learn_anyburl(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/run_anyburl.sh ' + work_dir)
    wait_until_file_is_saved(work_dir + "/rules/alpha-100", 60)


def predict_with_anyburl(work_dir):
    print("Predicting via AnyBURL...")
    os.system(f"java -Xmx10G -cp {work_dir}AnyBURL-JUNO.jar de.unima.ki.anyburl.Apply {work_dir}config-apply.properties")
    wait_until_file_is_saved(work_dir + "predictions/alpha-100_plog", 60)
    print("Evaluating AnyBURL...")
    os.system(f"java -Xmx10G -cp {work_dir}AnyBURL-JUNO.jar de.unima.ki.anyburl.Eval {work_dir}config-eval.properties > {work_dir}anyburl_eval.log")


def read_eval_result(work_dir):
    with open(work_dir + "anyburl_eval.log") as f:
        last_line = f.readlines()[-1].strip()
        scores = last_line.split()
        formated = f"hit@1, hit@3, hit@10, MRR\n" + "'".join(scores)
        return formated


def clean_anyburl(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_anyburl.sh ' + work_dir)


if __name__ == "__main__":
    read_hrt_pred_anyburl_2_hrt_int_df("../outputs/treat/anyburl/predictions/alpha-100")
