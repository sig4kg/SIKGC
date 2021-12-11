from abox_scanner.abox_utils import init_workdir
from module_utils.rumis_util import *
from module_utils.transE_util import *
from openKE import train_transe_NELL995
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from scripts import run_scripts
from module_utils.materialize_util import *


def prepare_context(work_dir, input_dir, schema_file, tbox_patterns_dir=""):
    init_workdir(work_dir)
    # prepare tbox patterns
    if tbox_patterns_dir == "" or not os.path.exists(tbox_patterns_dir):
        run_scripts.run_tbox_scanner(schema_file, work_dir)
        tbox_patterns_dir = work_dir + "tbox_patterns/"
    # mv data to work_dir
    os.system(f"cp {input_dir}* {work_dir}")
    # initialize context resource and check consistency
    context_resource = ContextResources(input_dir + "abox_hrt_uri.txt", class_and_op_file_path=work_dir, work_dir=work_dir, create_id_file=True)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_dir, context_resource)
    # first round scan, get ready for training
    abox_scanner_scheduler.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    read_scanned_2_context_df(work_dir, context_resource)
    return context_resource, abox_scanner_scheduler

def prepare_M(work_dir, schema_file):
    # Convert schema to DL-lite
    if not os.path.exists(work_dir + "tbox_dllite.ttl"):
            print("Converting schema to DL-Lite")
            scripts.run_scripts.to_dllite(schema_file, work_dir)
            wait_until_file_is_saved(work_dir + "tbox_dllite.ttl")
    else:
        print("Schema in DL-Lite exists: " + work_dir + "tbox_dllite.ttl")


def EC_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir):
    context_2_hrt_transE(work_dir, context_resource)
    train_count = len(context_resource.hrt_int_df.index)
    run_scripts.gen_pred_transE(work_dir)
    wait_until_train_pred_data_ready(work_dir)

    # 1.train transE
    train_transe_NELL995.train(work_dir + "train/")
    wait_until_file_is_saved(work_dir + "checkpoint/transe.ckpt")

    # 2. produce triples
    train_transe_NELL995.produce(work_dir + "train/", work_dir + "transE_raw_hrts.txt")
    wait_until_file_is_saved(work_dir + "transE_raw_hrts.txt", 30)

    # 3. consistency checking for new triples + old triples
    new_hrt_df = read_hrts_2_hrt_df(work_dir + "transE_raw_hrts.txt")
    to_scann_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
    # clean
    run_scripts.clean_tranE(work_dir)
    abox_scanner_scheduler.set_triples_to_scan_int_df(to_scann_hrt_df).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")

    # 4. get valid new triples
    new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")

    # 5. add new valid hrt to train data
    extend_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
    new_count = len(extend_hrt_df.index) - train_count
    rate = new_count / train_count
    print("update context data")
    context_resource.hrt_int_df = extend_hrt_df
    return rate


def RC_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir):
    # context int to rumis train
    train_count = len(context_resource.hrt_int_df.index)
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
    else:
        print("rumis one round done")

    # consistency checking for new triples
    new_hrt_df1 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.pos.10.needcheck", context_resource)
    new_hrt_df2 = read_hrt_rumis_2_hrt_int_df(work_dir + "DLV/extension.opm.kg.neg.10.needcheck", context_resource)
    new_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df1, new_hrt_df2], 0).drop_duplicates(keep='first').reset_index(drop=True)
    #  backup and clean last round data
    run_scripts.clean_rumis(work_dir=work_dir)
    abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
    # get valid new triples
    if wait_until_file_is_saved(work_dir + "valid_hrt.txt", 120):
        new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")
    else:
        print("saving time out, exit")

    # add new valid hrt to train set
    train_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
    new_count = len(new_hrt_df.index) - train_count
    rate = new_count / train_count
    # overwrite train data in context
    print("update context data")
    context_resource.hrt_int_df = train_hrt_df
    return rate


def M_block(context_resource:ContextResources, work_dir):
    # context int to materialization ntriples,
    train_count = len(context_resource.hrt_int_df.index)
    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
    wait_until_file_is_saved(work_dir + "abox.nt", 120)

    # the result is materialized_abox.nt
    print("running materialization...")
    materialize(work_dir)

    # read new data to context
    # we only keep entities in original abox. If node absent from original abox, we delete them.
    materialized_hrt_int_df = nt_2_hrt_int_df(work_dir + "cleaned_tbox_abox.nt", context_resource)
    print("update context data")
    context_resource.hrt_int_df = pd.concat([context_resource.hrt_int_df, materialized_hrt_int_df]).drop_duplicates(keep='first').reset_index(drop=True)
    #  backup and clean last round data
    run_scripts.clean_materialization(work_dir=work_dir)
    rate = (len(context_resource.hrt_int_df.index) - train_count) / train_count
    return rate
