from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources, TBOX_PATTERNS_PATH, ORIGINAL_TRIPLES_PATH
import pandas as pd
from scripts import run_scripts
import os
from tqdm import tqdm


def c_r_c(input_hrt_triple_file, work_dir, max_epoch=2):
    context_resource = ContextResources(input_hrt_triple_file, work_dir=work_dir, create_id_file=False)
    abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH, context_resource)
    abox_scanner_scheduler.register_pattern([1, 2])
    # first round scan, get ready for training
    abox_scanner_scheduler.scan_patterns(work_dir=work_dir)
    abox_utils.wait_until_file_is_saved(f"{work_dir}valid_hrt.txt", 30)
    os.system(f"mv {work_dir}valid_hrt.txt {work_dir}ideal.data.txt")
    with tqdm(total=max_epoch, colour="green") as pbar:
        for ep in range(max_epoch):
            pbar.set_description(f"R Triple Producer processing, round={ep}")
            run_scripts.run_rumis(work_dir)
            # consistency checking for new triples
            new_hrt_df1 = abox_utils.read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", context_resource)
            new_hrt_df2 = abox_utils.read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", context_resource)
            new_hrt_df = pd.concat([new_hrt_df1, new_hrt_df2], 0)
            abox_scanner_scheduler.set_triples_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
            # get valid new triples
            if abox_utils.wait_until_file_is_saved(work_dir + "valid_hrt.txt", 30):
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
            # overwrite train data
            abox_utils.hrt_int_df_2_hrt_rumis(train_hrt_df, context_resource, work_dir + "idea.data.txt")
            pbar.update(1)


if __name__ == "__main__":
    print("CRC pipeline")
    c_r_c(ORIGINAL_TRIPLES_PATH, "../outputs/rumis/")



