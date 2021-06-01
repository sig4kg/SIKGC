from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources, TBOX_PATTERNS_PATH, ORIGINAL_TRIPLES_PATH
from openKE import train_transe_NELL995
import pandas as pd


def c_t_c(input_hrt_triple_file, work_dir, max_epoch=2):
    context_resource = ContextResources(input_hrt_triple_file, work_dir=work_dir, create_id_file=True)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH, context_resource)

    abox_scanner_scheduler.register_pattern([1, 2])
    # first round scan, get ready for training
    abox_scanner_scheduler.scan_patterns(work_dir=work_dir)

    for ep in range(max_epoch):
        # train transE
        train_transe_NELL995.train(work_dir + "train/")
        # produce triples
        train_transe_NELL995.produce(work_dir + "train/", work_dir + "transE_raw_hrts.txt")
        train_count, old_hrt_df = abox_utils.read_htr_transE_2_hrt_df(work_dir + "train/train2id.txt")
        # consistency checking for new triples
        new_hrt_df = abox_utils.read_hrts_2_hrt_df(work_dir + "transE_raw_hrts.txt")
        abox_scanner_scheduler.set_triples_int(new_hrt_df.values.tolist()).scan_patterns(work_dir=work_dir)
        # get valid new triples
        new_hrt_df = abox_utils.read_hrt_2_df(work_dir + "valid_hrt.txt")
        new_count = new_hrt_df.count()
        # check rate
        if new_count / train_count < 0.001:
            break
        # add new valid hrt to train set
        train_hrt_df = pd.concat([old_hrt_df, new_hrt_df], axis=0)
        # overwrite train data
        abox_utils.hrt_df2htr_transE(train_hrt_df, work_dir + "train/train2id.txt")


if __name__ == "__main__":
    c_t_c(ORIGINAL_TRIPLES_PATH, "../outputs/")



