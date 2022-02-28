from tqdm.auto import trange
from pipeline_util import *


def clcmcac(work_dir, input_dir, schema_file, tbox_patterns_dir,
            loops=1, epoch=2, inductive=True, model="blp"):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    # prepare_M(work_dir, schema_file)
    prepare_blp(input_dir, work_dir + "L/")
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, nc1, nv1, ncc1 = LC_block(context_resource,
                                     abox_scanner_scheduler,
                                     work_dir + "L/",
                                     inductive=inductive,
                                     epoch=epoch,
                                     model=model)
        init_c2, extend_c2, nc2, nv2, ncc2 = M_block(context_resource, work_dir)
        init_c3, extend_c3, nc3, nv3, ncc3 = anyBURL_C_block(context_resource,
                                            abox_scanner_scheduler,
                                            work_dir + "A/")
        scores.append(get_scores(init_c1, extend_c3, nc1 + nc2 + nc3, nv1 + nv2 + nv3, ncc1 + ncc2 + ncc3))
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("clcmcac pipeline")
    clcmcac(work_dir="../outputs/clcmcac/", input_dir="../resources/TEST/",
            schema_file='../resources/NELL/NELL.ontology.nt',
            tbox_patterns_dir='../resources/NELL-patterns/')
