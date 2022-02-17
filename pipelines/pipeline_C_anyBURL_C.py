from abox_scanner import abox_utils
from pipeline_util import *
from tqdm.auto import trange


def c_anyburl_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1):
    run_scripts.delete_dir(anyburl_dir)
    context_resource, abox_scanner_scheduler = prepare_context(anyburl_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir, create_id_file=False)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        tc, nc, rate = anyBURL_C_Block(context_resource, abox_scanner_scheduler, anyburl_dir)
        if rate < 0.01:
            break
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)

if __name__ == "__main__":
    print("CRC pipeline")
    work_dir="../outputs/treat/"
    run_scripts.mk_dir(work_dir)
    anyburl_dir = work_dir + "anyburl/"
    c_anyburl_c(work_dir=anyburl_dir, input_dir="../resources/treat/",
                schema_file='../resources/treat/tbox.nt',
                tbox_patterns_dir='../resources/treat/tbox_patterns/')



