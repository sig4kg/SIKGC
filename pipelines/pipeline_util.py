from abox_scanner.abox_utils import init_dir, wait_until_file_is_saved
from materialize_util import materialize
from pipelines.ProducerBlock import PipelineConfig
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources
import os
import pandas as pd


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
        f_h2 = 2 * f_consistency * f_coverage2 / (f_coverage2 + f_consistency) if (f_coverage2 + f_consistency) > 0 else 0
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
    # prepare tbox patterns
    # if pipeline_config.tbox_patterns_dir == "" or not os.path.exists(pipeline_config.tbox_patterns_dir):
    #     run_scripts.run_tbox_scanner(pipeline_config.schema_file, work_dir)
    #     tbox_patterns_dir = work_dir + "tbox_patterns/"
    # mv data to work_dir
    os.system(f"cp {pipeline_config.input_dir}* {work_dir}")
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
        valids, invalids = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(work_dir=work_dir)
        abox_scanner_scheduler.scan_schema_correct_patterns(work_dir=work_dir)
        # wait_until_file_is_saved(work_dir + "valid_hrt.txt")
        context_resource.hrt_int_df = valids
    else:
        abox_scanner_scheduler.register_patterns_all()
        context_resource.hrt_int_df = context_resource.hrt_to_scan_df
    return context_resource, abox_scanner_scheduler


def prepare_schema_aware_silver_data(context_resource: ContextResources, pipeline_config: PipelineConfig):
    context_resource.to_ntriples(pipeline_config.work_dir, schema_in_nt=pipeline_config.schema_in_nt)
    wait_until_file_is_saved(pipeline_config.work_dir + "tbox_abox.nt", 120)
    print("running materialization...")
    pred_type_df, pred_hrt_df = materialize(pipeline_config.work_dir,
                                            context_resource,
                                            pipeline_config.reasoner,
                                            exclude_rels=pipeline_config.exclude_rels)
    groups = pred_type_df.groupby('head')
    ent2types = context_resource.entid2classids.copy(deep=True)
    for g in groups:
        ent = g[0]
        types = g[1]['tail'].tolist()
        if ent in ent2types:
            old_types = set(ent2types[ent])
            new_types = set(types)
            ent2types.update({ent: list(old_types | new_types)})

    new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).\
        drop_duplicates(keep="first").reset_index(drop=True)







