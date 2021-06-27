from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import TBOX_PATTERNS_PATH, ORIGINAL_TRIPLES_PATH, read_scanned_2_context_df, wait_until_file_is_saved
import pandas as pd
from scripts import run_scripts
import os
from tqdm.auto import trange
from abox_scanner.rumis_util import *


def c_r_c(input_hrt_triple_file, work_dir, max_epoch=2):
    context_resource = ContextResources(input_hrt_triple_file, work_dir=work_dir, create_id_file=False)
    abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH, context_resource)
    abox_scanner_scheduler.register_pattern([1, 2])
    # first round scan, get ready for training
    abox_scanner_scheduler.scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(f"{work_dir}valid_hrt.txt", 60)
    read_scanned_2_context_df(work_dir, context_resource)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        # context int to rumis train
        hrt_int_df_2_hrt_rumis(context_resource, work_dir + "ideal.data.txt")
        wait_until_file_is_saved(work_dir + "ideal.data.txt", 120)

        print("running rumis...")
        run_scripts.run_rumis(work_dir)
        check_result = wait_until_file_is_saved(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", 60) \
                       and wait_until_file_is_saved(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", 60)
        if not check_result:
            print({"no result from rumis producer, check logs"})
            break

        # consistency checking for new triples
        new_hrt_df1 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", context_resource)
        new_hrt_df2 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", context_resource)
        new_hrt_df = pd.concat([new_hrt_df1, new_hrt_df2], 0)
        abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)

        # get valid new triples
        if abox_utils.wait_until_file_is_saved(work_dir + "valid_hrt.txt", 120):
            new_hrt_df = abox_utils.read_hrt_2_df(work_dir + "valid_hrt.txt")
        else:
            print("saving time out, exit")

        # check rate
        # new_count = new_hrt_df.count()
        # if new_count / train_count < 0.001:
        #     break

        # add new valid hrt to train set
        old_hrt_df = context_resource.hrt_tris_int_df
        train_hrt_df = pd.concat([old_hrt_df, new_hrt_df], axis=0)

        #  backup and clean last round data
        run_scripts.clean_rumis(work_dir=work_dir)

        # overwrite train data in context
        context_resource.hrt_tris_int_df = train_hrt_df


if __name__ == "__main__":
    print("CRC pipeline")
    c_r_c("../resources/NELL-dev.txt", "../outputs/rumis/")



