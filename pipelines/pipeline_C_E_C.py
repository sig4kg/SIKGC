from tqdm.auto import trange
from pipeline_util import *


def c_e_c(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1, epoch=2, use_gpu=False, exclude_rels=[]):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir, create_id_file=True)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, new_count, new_valid_count, new_correct_count = EC_block(context_resource,
                                                                              abox_scanner_scheduler,
                                                                              work_dir,
                                                                              epoch=epoch,
                                                                              exclude_rels=exclude_rels,
                                                                              use_gpu=use_gpu)
        scores_dict = get_scores(init_c1, extend_c1, new_count, new_valid_count, new_correct_count)
        scores.append(scores_dict)
    context_resource.to_ntriples(work_dir)
    return scores









