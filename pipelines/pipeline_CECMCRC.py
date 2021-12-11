from tqdm.auto import trange
from pipeline_util import *


def cecmcrc(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=2):
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file, tbox_patterns_dir=tbox_patterns_dir)
    prepare_M(work_dir, schema_file)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        rate1 = EC_block(context_resource, abox_scanner_scheduler, work_dir)
        rate2 = M_block(context_resource, work_dir)
        rate3 = RC_block(context_resource, abox_scanner_scheduler, work_dir)
        if rate3 < 0:
            break
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("cecmcrc pipeline")
    cecmcrc(work_dir="../outputs/cecmcrc/", input_dir="../resources/TEST/",
        schema_file='../resources/NELL/NELL.ontology.nt',
            tbox_patterns_dir= '../resources/NELL-patterns/')






