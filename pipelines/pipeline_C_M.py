from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import read_scanned_2_context_df, wait_until_file_is_saved, ContextResources
from scripts import run_scripts
from tqdm.auto import trange
from module_utils.materialize_util import *
from pipeline_util import *


def c_m(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1, schema_in_nt=''):
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    # prepare_M(work_dir, schema_file)
    get_scores = aggregate_scores()
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, new_count, new_valid_count, new_correct_count = M_block(context_resource, work_dir, schema_in_nt=schema_in_nt)
        scores.append(get_scores(init_c1, extend_c1, new_count, new_valid_count, new_correct_count))
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores



if __name__ == "__main__":
    print("CM pipeline")
    c_m(work_dir="../outputs/cm/",
        input_dir="../resources/TEST/",
        schema_file='../resources/TEST/NELL.ontology.ttl',
        tbox_patterns_dir='../resources/NELL-patterns/',
        schema_in_nt='../resources/NELL/tbox.nt')





