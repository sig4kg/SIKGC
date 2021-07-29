from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import *
from abox_scanner.blp_util import *
from openKE import train_transe_NELL995
import pandas as pd
from scripts import run_scripts
from tqdm.auto import trange
from blp.producer import ex

def c_l_c(input_hrt_raw_triple_file, work_dir, max_epoch=2):
    context_resource = ContextResources(input_hrt_raw_triple_file, work_dir=work_dir, create_id_file=True)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    # abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH, context_resource)
    # first round scan, get ready for training
    # abox_scanner_scheduler.register_pattern([1, 2]).scan_patterns(work_dir=work_dir)
    # wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    # read_scanned_2_context_df(work_dir, context_resource)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        hrt_int_df_2_hrt_blp(context_resource, work_dir)    # generate all_triples.tsv, entities.txt, relations.txt\
        wait_until_blp_data_ready(work_dir)

        # 1. run blp
        ex.run(config_updates={'work_dir': work_dir, 'inductive': False})
        wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)

        # 2. consistency checking for new triples
        pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource)
        new_hrt_df = pd.concat([pred_hrt_df, context_resource.hrt_tris_int_df, context_resource.hrt_tris_int_df]).\
            drop_duplicates(keep=False) # diff
        hit_hrt_df = pd.merge(pred_hrt_df, context_resource.hrt_tris_int_df, how="inner")

        # run_scripts.clean_tranE(work_dir)
        # abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
        # wait_until_file_is_saved(work_dir + "valid_hrt.txt")

        # 3. get valid new triples
        # new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")
        # new_count = len(new_hrt_df)

        # 4. check rate
        # train_count = len(context_resource.hrt_tris_int_df)
        # if new_count / train_count < 0.001:
        #     break

        # 5. add new valid hrt to train data
        extend_hrt_df = pd.concat([context_resource.hrt_tris_int_df, new_hrt_df], axis=0)
        context_resource.hrt_tris_int_df = extend_hrt_df

if __name__ == "__main__":
    print("CLC pipeline")
    c_l_c("../outputs/umls/all_triples.tsv", "../outputs/umls/")







