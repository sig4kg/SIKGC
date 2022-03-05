from tqdm.auto import trange
from pipeline_util import *


def c_l_c(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1, epoch=5,
          inductive=False, model='transductive', lr=3e-5,
          use_scheduler=True,
          batch_size=64,
          emb_batch_size=1024,
          eval_batch_size=64,
          exclude_rels=[]):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    prepare_blp(input_dir, work_dir)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, new_count, new_valid_count, new_correct_count = LC_block(context_resource,
                                                                                     abox_scanner_scheduler,
                                                                                     work_dir,
                                                                                     inductive=inductive,
                                                                                     lr=lr,
                                                                                     use_scheduler=use_scheduler,
                                                                                     batch_size=batch_size,
                                                                                     emb_batch_size=emb_batch_size,
                                                                                     eval_batch_size=eval_batch_size,
                                                                                     epoch=epoch,
                                                                                     exclude_rels=exclude_rels,
                                                                                     model=model)

        scores_dict = get_scores(init_c1, extend_c1, new_count, new_valid_count, new_correct_count)
        scores.append(scores_dict)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores
