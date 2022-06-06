import random

import file_util
import scripts.run_scripts
from abox_scanner.abox_utils import wait_until_file_is_saved
from module_utils.materialize_util import materialize
from pipelines.ProducerBlock import PipelineConfig
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources
import os
import pandas as pd
from module_utils.sample_util import split_relation_triples, split_type_triples


def get_block_names(name_in_short: str):
    capital_names = name_in_short.upper().strip().split('_')
    supported = ['M', 'A', 'L']
    if any([x not in supported for x in capital_names]):
        print("Unsupported pipeline, please use pipeline names as a_l_m, m_a_l etc.")
        return []
    else:
        return capital_names


def aggregate_scores():
    init_kgs, target_kgs, nc, vc, cc, n = [], [], [], [], [], [0]

    def add_new(init_kgc, extend_kgc, new_count, new_valid_count, new_correct_count):
        n[0] = n[0] + 1
        nc.append(new_count)
        vc.append(new_valid_count)
        cc.append(new_correct_count)
        init_kgs.append(init_kgc)
        target_kgs.append(extend_kgc)
        tf_correctness = 0
        tf_consistency = 0
        ta = 0
        ty = 0
        total_new = 0
        for i in range(n[0]):
            if nc[i] == 0:
                continue
            tf_correctness += (cc[i] / nc[i])
            tf_consistency += (vc[i] / nc[i])
            ta += cc[i]
            ty += vc[i]
            total_new += nc[i]

        f_correctness = tf_correctness / n[0]
        f_coverage = ta / init_kgs[0]
        f_h = 2 * f_correctness * f_coverage / (f_coverage + f_correctness) if (f_coverage + f_correctness) > 0 else 0
        f_consistency = tf_consistency / n[0]
        f_coverage2 = ty / init_kgs[0]
        f_h2 = 2 * f_consistency * f_coverage2 / (f_coverage2 + f_consistency) if (
                                                                                          f_coverage2 + f_consistency) > 0 else 0
        result = {"init_kgs": init_kgs,
                  "target_kgs": target_kgs,
                  "new_count": nc,
                  "new_valid_count": vc,
                  "new_correct_count": cc,
                  "f_correctness": f_correctness,
                  "f_coverage": f_coverage,
                  "f_correctness_coverage": f_h,
                  "f_consistency": f_consistency,
                  "f_coverage2": f_coverage2,
                  "f_consistency_coverage": f_h2}
        for key in result:
            print(f"{key}: {result[key]}")
        return result

    return add_new


def prepare_context(pipeline_config: PipelineConfig, consistency_check=True, abox_file_hrt=""):
    work_dir = pipeline_config.work_dir
    # if pipeline_config.tbox_patterns_dir == "" or not os.path.exists(pipeline_config.tbox_patterns_dir):
    #     run_scripts.run_tbox_scanner(pipeline_config.schema_file, work_dir)
    #     tbox_patterns_dir = work_dir + "tbox_patterns/"
    # mv data to work_dir
    os.system(f"cp -rf {pipeline_config.input_dir}* {work_dir}")
    # initialize context resource and check consistency
    if abox_file_hrt != "":
        abox_file_path = abox_file_hrt
    else:
        abox_file_path = pipeline_config.input_dir + "abox_hrt_uri.txt"
    context_resource = ContextResources(abox_file_path, class_and_op_file_path=work_dir,
                                        work_dir=work_dir)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(pipeline_config.tbox_patterns_dir, context_resource)
    # first round scan, get ready for training
    if consistency_check:
        if not file_util.does_file_exist(pipeline_config.work_dir + 'valid_hrt.txt'):
            valids, _ = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(work_dir=work_dir, save_result=False)
        else:
            valids = file_util.read_hrt_2_hrt_int_df(pipeline_config.work_dir + 'valid_hrt.txt')
        context_resource.hrt_int_df = valids
    else:
        abox_scanner_scheduler.register_patterns_all()
        context_resource.hrt_int_df = context_resource.hrt_to_scan_df

    # schema-aware sampling
    if pipeline_config.blp_config['schema_aware']:
        if not file_util.does_file_exist(pipeline_config.work_dir + 'random_invalid_hrt.txt'):
            generate_random_invalids(context_resource, abox_scanner_scheduler, pipeline_config.work_dir)

        # schema_aware silver evaluation, we freeze a small portion of test data and keep them in context_resource
    if pipeline_config.silver_eval:
        freeze_silver_test_data(context_resource, pipeline_config)
    return context_resource, abox_scanner_scheduler


def generate_random_invalids(context_resource: ContextResources, abox_scanner_scheduler: AboxScannerScheduler, work_dir):
    valids = context_resource.hrt_int_df
    candidate_ents = context_resource.id2ent.keys()
    corrupt = pd.DataFrame()
    corrupt['c_h'] = valids['head'].apply(func=lambda x: random.sample(candidate_ents, 8))
    corrupt['rel'] = valids['rel']
    corrupt['c_t'] = valids['tail'].apply(func=lambda x: random.sample(candidate_ents, 8))
    corrupt.reset_index(drop=True)

    def explode(tmp_df, col, rename_col) -> pd.DataFrame:
        tmp_df[col] = tmp_df[col].apply(lambda x: list(x))
        tm = pd.DataFrame(list(tmp_df[col])).stack().reset_index(level=0)
        tm = tm.rename(columns={0: rename_col}).join(tmp_df, on='level_0'). \
            drop(axis=1, labels=[col, 'level_0']).reset_index(drop=True)
        return tm

    corrupt = explode(corrupt, "c_h", "head").dropna(how='any')
    corrupt = explode(corrupt, "c_t", "tail")
    corrupt = corrupt[['head', 'rel', 'tail']].dropna(how='any').astype('int64')
    to_scan_df = pd.concat([context_resource.hrt_int_df, corrupt]).drop_duplicates(keep="first").reset_index(
        drop=True)
    context_resource.hrt_to_scan_df = to_scan_df
    v, inv = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(work_dir=work_dir, save_result=False)
    inv.to_csv(f"{work_dir}random_invalid_hrt.txt", header=False, index=False, sep='\t', mode='a')
    wait_until_file_is_saved(f'{work_dir}random_invalid_hrt.txt')


def split_schema_aware_silver_data(context_resource: ContextResources, pipeline_config: PipelineConfig):
    context_resource.to_ntriples(pipeline_config.work_dir, schema_in_nt=pipeline_config.schema_in_nt)
    wait_until_file_is_saved(pipeline_config.work_dir + "tbox_abox.nt", 120)
    print("running materialization...")
    pred_hrt_df, pred_type_df = materialize(pipeline_config.work_dir,
                                            context_resource,
                                            pipeline_config.reasoner,
                                            exclude_rels=pipeline_config.exclude_rels)
    groups = pred_type_df.groupby('head')
    ent2types = context_resource.entid2classids.copy()
    for g in groups:
        ent = g[0]
        types = g[1]['tail'].tolist()
        if ent in ent2types:
            old_types = set(ent2types[ent])
            new_types = set(types)
            ent2types.update({ent: list(old_types | new_types)})

    new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]). \
        drop_duplicates(keep=False).reset_index(drop=True)

    df_rel_train, df_rel_test, _ = split_relation_triples(hrt_df=context_resource.hrt_int_df,
                                                          exclude_rels=pipeline_config.exclude_rels,
                                                          produce=False)
    dict_type_train, dict_type_test, _ = split_type_triples(context_resource=context_resource,
                                                            top_n_types=50,
                                                            produce=False)
    silver_rel_test = pd.concat([df_rel_test, new_hrt_df]).drop_duplicates(keep='first').reset_index(drop=True)
    silver_type_dict = {ent: ent2types[ent] for ent in dict_type_test}
    dict_type_train = {ent: ent2types[ent] for ent in dict_type_train}
    splited = {'rel_test': silver_rel_test,
               'type_test': silver_type_dict,
               'rel_train': df_rel_train,
               'type_train': dict_type_train}
    return splited


# this function split a portion of test data and extend with materialization data.
# the left data will be set to context_resource
def freeze_silver_test_data(context_resource: ContextResources, pipeline_config: PipelineConfig):
    if file_util.does_file_exist(pipeline_config.work_dir + "silver_rel.csv"):
        silver_rel = file_util.read_hrt_2_hrt_int_df(pipeline_config.work_dir + "silver_rel.csv")
        silver_rel_train = file_util.read_hrt_2_hrt_int_df(pipeline_config.work_dir + "silver_rel_train.csv")
        silver_type_test = file_util.read_type_dict(pipeline_config.work_dir + "silver_type_test.csv")
        silver_type_train = file_util.read_type_dict(pipeline_config.work_dir + "silver_type_train.csv")
        context_resource.silver_rel = silver_rel
        context_resource.hrt_int_df = silver_rel_train
        context_resource.silver_type = silver_type_test
        context_resource.silver_type_train = silver_type_train
    else:
        splited = split_schema_aware_silver_data(context_resource, pipeline_config)
        context_resource.hrt_int_df = splited['rel_train']
        context_resource.silver_rel = splited['rel_test']
        context_resource.silver_type = splited['type_test']
        context_resource.silver_type_train = splited['type_train']
        splited['rel_test'].to_csv(pipeline_config.work_dir + "silver_rel.csv", header=False, index=False, sep='\t')
        splited['rel_train'].to_csv(pipeline_config.work_dir + "silver_rel_train.csv", header=False, index=False, sep='\t')
        file_util.write_type_dict(splited['type_test'], pipeline_config.work_dir + "silver_type_test.csv")
        file_util.write_type_dict(splited['type_train'], pipeline_config.work_dir + "silver_type_train.csv")

