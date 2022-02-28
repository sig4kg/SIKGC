from pipeline_util import *
from tqdm.auto import trange


def c_anyburl_c(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir, create_id_file=False)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        train_count, new_count, new_valid_count, new_correct_count = anyBURL_C_block(context_resource, abox_scanner_scheduler, work_dir)
        scores_dict = get_scores(new_count, new_valid_count, new_correct_count)
        scores.append(scores_dict)
        if new_valid_count / train_count < 0.01:
            break
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores


if __name__ == "__main__":
    print("CRC pipeline")




