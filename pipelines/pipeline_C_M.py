from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import read_scanned_2_context_df, wait_until_file_is_saved, ContextResources
from scripts import run_scripts
from tqdm.auto import trange
from module_utils.materialize_util import *
from pipeline_util import *


def c_m(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1):
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    prepare_M(work_dir, schema_file)
    scores = []
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        f_correctness, f_coverage, f_h = M_block(context_resource, work_dir)
        scores.append((f_correctness, f_coverage, f_h))
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores



if __name__ == "__main__":
    print("CM pipeline")
    c_m(work_dir="../outputs/cm/",
        input_dir="../resources/NELL/",
        schema_file='../resources/NELL/NELL.ontology.nt',
        tbox_patterns_dir='../resources/NELL-patterns/')





