from tqdm.auto import trange
from pipeline_util import *


def clcmcac(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=2):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    prepare_M(work_dir, schema_file)
    prepare_blp(input_dir, work_dir + "L/")
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        _, nc1, nv1, ncc1 = LC_block(context_resource, abox_scanner_scheduler, work_dir + "L/")
        _, nc2 = M_block(context_resource, work_dir)
        _, nc3, nv3, ncc3 = anyBURL_C_block(context_resource, abox_scanner_scheduler, work_dir + "A/")
        get_scores(nc1 + nc2 + nc3, nv1 + nc2 + nv3, ncc1 + nc2 + ncc3)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("cecmcrc pipeline")
    clcmcac(work_dir="../outputs/clcmcac/", input_dir="../resources/TEST/",
            schema_file='../resources/NELL/NELL.ontology.nt',
            tbox_patterns_dir='../resources/NELL-patterns/')
