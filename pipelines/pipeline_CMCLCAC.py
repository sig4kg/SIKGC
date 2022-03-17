from tqdm.auto import trange
from pipeline_util import *


def cmclcac(work_dir, input_dir, schema_file, tbox_patterns_dir,
            loops=1, exclude_rels=[], blp_config={}, schema_in_nt=""):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    # prepare_M(work_dir, schema_file)
    prepare_blp(input_dir, work_dir + "L/")
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c2, extend_c2, nc2, nv2, ncc2 = M_block(context_resource,
                                                     abox_scanner_scheduler,
                                                     work_dir,
                                                     schema_in_nt=schema_in_nt)
        init_c1, extend_c1, nc1, nv1, ncc1 = LC_block(context_resource,
                                                      abox_scanner_scheduler,
                                                      work_dir + "L/",
                                                      exclude_rels=exclude_rels,
                                                      blp_config=blp_config)
        init_c3, extend_c3, nc3, nv3, ncc3 = anyBURL_C_block(context_resource,
                                                             abox_scanner_scheduler,
                                                             work_dir + "A/",
                                                             exclude_rels=exclude_rels)
        s = get_scores(init_c1, extend_c3 + context_resource.new_type_count, nc1 + nc2 + nc3, nv1 + nv2 + nv3, ncc1 + ncc2 + ncc3)
        scores.append(s)
    context_resource.to_ntriples(work_dir)
    return scores
