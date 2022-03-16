from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import wait_until_file_is_saved
from scripts import run_scripts
from tqdm.auto import trange
from module_utils.rumis_util import *
from pipeline_util import *


def c_rumis_c(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1):
    run_scripts.delete_dir(work_dir)
    get_scores = aggregate_scores()
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        init_c1, extend_c1, new_count, new_valid_count, new_correct_count = Rumis_C_block(context_resource, abox_scanner_scheduler, work_dir)
        scores.append(get_scores(init_c1, extend_c1, new_count, new_valid_count, new_correct_count))
    context_resource.to_ntriples(work_dir)
    return scores


if __name__ == "__main__":
    # print("CRC pipeline")
    # c_rumis_c(work_dir="../outputs/crc/",
    #       input_dir="../resources/TEST/",
    #       schema_file='../resources/NELL/NELL.ontology.nt',
    #       tbox_patterns_dir='../resources/NELL-patterns/')
    ss = aggregate_scores();
    tt1 = ss(2,1,1)
    tt2 = ss(3,0,0)
    tt3 = ss(0,0,0)
    tt4 = ss(2,1,0)
    tt5 =ss(2,2,1)



