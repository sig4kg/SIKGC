from tqdm.auto import trange
from pipeline_util import *


def c_e_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=2, use_gpu=False):
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        tc, nc, rate = EC_block(context_resource, abox_scanner_scheduler, work_dir, use_gpu=use_gpu)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("CEC pipeline")
    c_e_c(work_dir="../outputs/cecmcrc/",
          input_dir="../resources/TEST/",
          schema_file='../resources/NELL/NELL.ontology.nt',
          tbox_patterns_dir='../resources/NELL-patterns/')







