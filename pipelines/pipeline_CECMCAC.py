from tqdm.auto import trange
from pipeline_util import *


def cecmcac(work_dir, input_dir, schema_file, tbox_patterns_dir,
            loops=1, epoch=2, use_gpu=False, exclude_rels=[]):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    # prepare_M(work_dir, schema_file)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, nc1, nv1, ncc1 = EC_block(context_resource,
                                                      abox_scanner_scheduler,
                                                      work_dir,
                                                      epoch=epoch,
                                                      use_gpu=use_gpu,
                                                      exclude_rels=exclude_rels)
        init_c2, extend_c2, nc2, nv2, ncc2 = M_block(context_resource, work_dir)
        init_c3, extend_c3, nc3, nv3, ncc3 = anyBURL_C_block(context_resource,
                                                             abox_scanner_scheduler,
                                                             work_dir + "A/",
                                                             exclude_rels=exclude_rels)
        s = get_scores(init_c1, extend_c3, nc1 + nc2 + nc3, nv1 + nv2 + nv3, ncc1 + ncc2 + ncc3)
        scores.append(s)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores


