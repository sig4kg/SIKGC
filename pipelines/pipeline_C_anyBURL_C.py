from pipeline_util import *
from tqdm.auto import trange


def c_anyburl_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir, create_id_file=False)
    scores = []
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        train_count, new_count, new_valid_count, new_correct_count = anyBURL_C_block(context_resource, abox_scanner_scheduler, work_dir)
        f_correctness, f_coverage, f_h = get_scores(new_count, new_valid_count, new_correct_count)
        scores.append((f_correctness, f_coverage, f_h))
        if new_valid_count / train_count < 0.01:
            break
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores


if __name__ == "__main__":
    print("CRC pipeline")
    wd="../outputs/treat/"
    run_scripts.mk_dir(wd)
    anyburl_dir = wd + "anyburl/"
    c_anyburl_c(work_dir=anyburl_dir, input_dir="../resources/treat/",
                schema_file='../resources/treat/tbox.nt',
                tbox_patterns_dir='../resources/treat/tbox_patterns/')



