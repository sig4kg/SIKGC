from tqdm.auto import trange
from pipeline_util import *


def c_l_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1, inductive=False, model='transductive'):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    prepare_blp(input_dir, work_dir)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        train_count, new_count, new_valid_count, new_correct_count = LC_block(context_resource, abox_scanner_scheduler, work_dir, inductive=inductive, model=model)
        get_scores(new_count, new_valid_count, new_correct_count)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("CLC pipeline")
    # c_l_c(work_dir="../outputs/log_clc/",
    #       input_dir="../resources/treat/",
    #       schema_file='../resources/treat/tbox.nt',
    #       tbox_patterns_dir='../resources/treat/tbox_patterns/')
    c_l_c(work_dir="../outputs/clc/",
          input_dir="../resources/TEST/",
          schema_file='../resources/NELL/NELL.ontology.nt',
          tbox_patterns_dir='../resources/NELL-patterns/')
          # inductive=True,
          # model='bert-bow')