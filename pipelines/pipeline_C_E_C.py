from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import *
from module_utils.transE_util import *
from openKE import train_transe_NELL995
import pandas as pd
from scripts import run_scripts
from tqdm.auto import trange


def c_e_c(input_hrt_raw_triple_file, work_dir, class_op_and_pattern_path, max_epoch=1):
    context_resource = ContextResources(input_hrt_raw_triple_file, work_dir=work_dir, class_and_op_file_path=class_op_and_pattern_path, create_id_file=True)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(class_op_and_pattern_path, context_resource)
    # first round scan, get ready for training
    abox_scanner_scheduler.register_pattern([1, 2]).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    read_scanned_2_context_df(work_dir, context_resource)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        context_2_hrt_transE(work_dir, context_resource)
        train_count = len(context_resource.hrt_int_df)
        run_scripts.gen_pred_transE(work_dir)
        wait_until_train_pred_data_ready(work_dir)

        # 1.train transE
        train_transe_NELL995.train(work_dir + "train/")
        wait_until_file_is_saved(work_dir + "checkpoint/transe.ckpt")

        # 2. produce triples
        train_transe_NELL995.produce(work_dir + "train/", work_dir + "transE_raw_hrts.txt")
        wait_until_file_is_saved(work_dir + "transE_raw_hrts.txt", 30)

        # 3. consistency checking for new triples
        new_hrt_df = read_hrts_2_hrt_df(work_dir + "transE_raw_hrts.txt")
        run_scripts.clean_tranE(work_dir)
        abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
        wait_until_file_is_saved(work_dir + "valid_hrt.txt")

        # 4. get valid new triples
        new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")
        new_count = len(new_hrt_df)

        # 5. check rate
        if new_count / train_count < 0.001:
            break

        # 6. add new valid hrt to train data
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0)
        context_resource.hrt_int_df = extend_hrt_df


if __name__ == "__main__":
    print("CTC pipeline")
    c_e_c("../resources/DBpedia-politics/PoliticalTriplesWD.txt", "../outputs/cec/", class_op_and_pattern_path='../resources/DBpedia-politics/tbox-dbpedia/')







