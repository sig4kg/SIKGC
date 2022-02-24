from pipeline_util import *
from tqdm.auto import trange


def c_anyburl_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir, create_id_file=False)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        train_count, new_count, new_valid_count, new_correct_count = anyBURL_C_block(context_resource, abox_scanner_scheduler, anyburl_dir)
        get_scores(new_count, new_valid_count, new_correct_count)
        if new_valid_count / train_count < 0.01:
            break
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)

if __name__ == "__main__":
    print("CRC pipeline")
    wd="../outputs/treat/"
    run_scripts.mk_dir(wd)
    anyburl_dir = wd + "anyburl/"
    c_anyburl_c(work_dir=anyburl_dir, input_dir="../resources/treat/",
                schema_file='../resources/treat/tbox.nt',
                tbox_patterns_dir='../resources/treat/tbox_patterns/')
    # get_scores = aggregate_scores(0, 0, 0)
    # get_scores(1,1,1)
    # get_scores(2,1,1)
    # get_scores(3,2,1)


# def generate_counter(prefix: str, count_start=-1):
#     count = [count_start]
#     def add_one():
#         count[0] = count[0] + 1
#         return prefix + '_' + str(count[0])
#     return add_one



