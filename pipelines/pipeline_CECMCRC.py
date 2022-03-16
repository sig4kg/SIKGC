from tqdm.auto import trange
from pipeline_util import *


def cecmcrc(work_dir, input_dir, schema_file, tbox_patterns_dir, epoch=2, loops=1, use_gpu=False, exclude_rels=[]):
    get_scores = aggregate_scores()
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir,
                                                               create_id_file=True)
    # prepare_M(work_dir, schema_file)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, nc1, nv1, ncc1 = EC_block(context_resource,
                                                      abox_scanner_scheduler,
                                                      work_dir,
                                                      epoch=epoch,
                                                      use_gpu=use_gpu,
                                                      exclude_rels=exclude_rels)
        init_c2, extend_c2, nc2, nv2, ncc2 = M_block(context_resource, work_dir)
        init_c3, extend_c3, nc3, nv3, ncc3 = Rumis_C_block(context_resource, abox_scanner_scheduler, work_dir + "R/")
        scores.append(get_scores(init_c1, extend_c3, nc1 + nc2 + nc3, nv1 + nv2 + nv3, ncc1 + ncc2 + ncc3))
    context_resource.to_ntriples(work_dir)
    return scores


if __name__ == "__main__":
    print("cecmcrc pipeline")
    cecmcrc(work_dir="../outputs/cecmcrc/", input_dir="../resources/TEST/",
            schema_file='../resources/NELL/tbox.nt',
            tbox_patterns_dir='../resources/NELL-patterns/')
