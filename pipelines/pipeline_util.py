from abox_scanner.abox_utils import *
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.rumis_util import *
from abox_scanner.transE_util import *
from scripts import run_scripts
from openKE import train_transe_NELL995


def init_context(input_hrt_raw_triple_file, work_dir):
    context_resource = ContextResources(input_hrt_raw_triple_file, work_dir=work_dir, create_id_file=True)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH, context_resource)
    # first round scan, get ready for training
    abox_scanner_scheduler.register_pattern([1, 2]).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    read_scanned_2_context_df(work_dir, context_resource)


def T_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir):
    context_2_hrt_transE(work_dir, context_resource)
    train_count = len(context_resource.hrt_tris_int_df)
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

    # 5. add new valid hrt to train data
    extend_hrt_df = pd.concat([context_resource.hrt_tris_int_df, new_hrt_df], axis=0)
    context_resource.hrt_tris_int_df = extend_hrt_df

    return new_count / train_count


def R_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir):
    hrt_int_df_2_hrt_rumis(context_resource, work_dir + "ideal.data.txt")
    wait_until_file_is_saved(work_dir + "ideal.data.txt", 120)

    print("running rumis...")
    run_scripts.run_rumis(work_dir)
    check_result = wait_until_file_is_saved(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", 60) \
                   and wait_until_file_is_saved(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", 60)
    if not check_result:
        print({"no result from rumis producer, check logs"})
        run_scripts.clean_rumis(work_dir=work_dir)
        return -1

    # consistency checking for new triples
    new_hrt_df1 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", context_resource)
    new_hrt_df2 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", context_resource)
    new_hrt_df = pd.concat([new_hrt_df1, new_hrt_df2], 0)
    abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)

    # get valid new triples
    if wait_until_file_is_saved(work_dir + "valid_hrt.txt", 120):
        new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")
        new_count = len(new_hrt_df)
    else:
        print("saving time out, exit")
        run_scripts.clean_rumis(work_dir=work_dir)
        return -1

    # check rate
    # new_count = new_hrt_df.count()
    # if new_count / train_count < 0.001:
    #     break

    # add new valid hrt to train set
    old_hrt_df = context_resource.hrt_tris_int_df
    old_count = len(old_hrt_df)
    train_hrt_df = pd.concat([old_hrt_df, new_hrt_df], axis=0)

    #  backup and clean last round data
    run_scripts.clean_rumis(work_dir=work_dir)

    # overwrite train data in context
    context_resource.hrt_tris_int_df = train_hrt_df
    return new_count / old_count


def M_block(context_resource:ContextResources, work_dir):
    pass
