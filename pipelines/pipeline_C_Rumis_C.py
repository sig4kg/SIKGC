from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import read_scanned_2_context_df, wait_until_file_is_saved
from scripts import run_scripts
from tqdm.auto import trange
from module_utils.rumis_util import *
from pipeline_util import *


def c_rumis_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1):
    run_scripts.delete_dir(work_dir)
    get_scores = aggregate_scores()
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    scores = []
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        train_count, new_count, new_valid_count, new_correct_count = Rumis_C_block(context_resource, abox_scanner_scheduler, work_dir)
        scores.append(get_scores(new_count, new_valid_count, new_correct_count))
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    return scores


if __name__ == "__main__":
    print("CRC pipeline")
    c_rumis_c(work_dir="../outputs/crc/",
          input_dir="../resources/NELL/",
          schema_file='../resources/NELL/NELL.ontology.nt',
          tbox_patterns_dir='../resources/NELL-patterns/')



