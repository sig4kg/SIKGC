from abox_scanner.abox_utils import init_workdir
from module_utils.rumis_util import *
from module_utils.transE_util import *
from openKE import train_transe_NELL995
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from scripts import run_scripts
from module_utils.materialize_util import *
from module_utils.blp_util import *
from blp.producer import ex
from scripts.run_scripts import clean_blp
from module_utils.anyburl_util import *


def prepare_context(work_dir, input_dir, schema_file, tbox_patterns_dir="", consistency_check=True, create_id_file=True):
    init_workdir(work_dir)
    # prepare tbox patterns
    if tbox_patterns_dir == "" or not os.path.exists(tbox_patterns_dir):
        run_scripts.run_tbox_scanner(schema_file, work_dir)
        tbox_patterns_dir = work_dir + "tbox_patterns/"
    # mv data to work_dir
    os.system(f"cp {input_dir}* {work_dir}")
    # initialize context resource and check consistency
    context_resource = ContextResources(input_dir + "abox_hrt_uri.txt", class_and_op_file_path=work_dir, work_dir=work_dir, create_id_file=create_id_file)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_dir, context_resource)
    # first round scan, get ready for training
    if consistency_check:
        abox_scanner_scheduler.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]).scan_patterns(work_dir=work_dir)
        wait_until_file_is_saved(work_dir + "valid_hrt.txt")
        read_scanned_2_context_df(work_dir, context_resource)
    else:
        abox_scanner_scheduler.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13])
        context_resource.hrt_int_df = context_resource.hrt_to_scan_df
    return context_resource, abox_scanner_scheduler

def prepare_M(work_dir, schema_file):
    # Convert schema to DL-lite
    if not os.path.exists(work_dir + "tbox_dllite.ttl"):
            print("Converting schema to DL-Lite")
            scripts.run_scripts.to_dllite(schema_file, work_dir)
            wait_until_file_is_saved(work_dir + "tbox_dllite.ttl")
    else:
        print("Schema in DL-Lite exists: " + work_dir + "tbox_dllite.ttl")


def EC_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir, use_gpu=False):
    context_2_hrt_transE(work_dir, context_resource)
    train_count = len(context_resource.hrt_int_df.index)
    run_scripts.gen_pred_transE(work_dir)
    wait_until_train_pred_data_ready(work_dir)

    # 1.train transE
    train_transe_NELL995.train(work_dir + "train/", use_gpu=use_gpu)
    wait_until_file_is_saved(work_dir + "checkpoint/transe.ckpt")

    # 2. produce triples
    train_transe_NELL995.produce(work_dir + "train/", work_dir + "transE_raw_hrts.txt", use_gpu=use_gpu)
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


def LC_block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir, inductive=False):
    hrt_int_df_2_hrt_blp(context_resource, work_dir, triples_only=False)    # generate all_triples.tsv, entities.txt, relations.txt\
    wait_until_file_is_saved(work_dir + "all_triples.tsv")
    split_all_triples(work_dir, inductive=inductive) # split all_triples.tsv to train.tsv, dev.tsv, takes time
    wait_until_blp_data_ready(work_dir, inductive=inductive)
    # 1. run blp
    ex.run(config_updates={'work_dir': work_dir,
                           'dataset': 'treat',
                           'inductive': inductive,
                           "do_downstream_sample": True,
                           'max_epochs':2,
                           'model': "transductive"})
    wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)

    # 2. consistency checking for new triples
    pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource)
    print("all produced triples: " + str(len(pred_hrt_df)))
    # diff
    new_hrt_df = pd.concat([pred_hrt_df.drop_duplicates(keep='first'), context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(keep=False)
    print("all old triples: " + str(len(context_resource.hrt_int_df)))
    print("all new triples: " + str(len(new_hrt_df)))

    # 3. get valid new triples
    clean_blp(work_dir)
    abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")

    # 4. check rate
    new_count = len(new_hrt_df)
    train_count = len(context_resource.hrt_int_df)
    rate = new_count / train_count

    # 5. add new valid hrt to train data
    extend_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first')
    context_resource.hrt_int_df = extend_hrt_df
    return rate


def anyBURL_C_Block(context_resource:ContextResources, abox_scanner_scheduler:AboxScannerScheduler, work_dir):
    hrt_int_df_2_hrt_anyburl(context_resource, work_dir)
    prepare_anyburl_configs(work_dir)
    split_all_triples_anyburl(work_dir)
    wait_until_anyburl_data_ready(work_dir)
    print("running anyBURL...")
    run_scripts.run_anyburl(work_dir)
    wait_until_file_is_saved(work_dir + "predictions/alpha-100", 60)

    # consistency checking for new triples
    new_hrt_df = read_hrt_pred_anyburl_2_hrt_int_df(work_dir + "predictions/alpha-100", context_resource)
    #  backup and clean last round data
    run_scripts.clean_anyburl(work_dir=work_dir)
    abox_scanner_scheduler.set_triples_to_scan_int_df(new_hrt_df).scan_patterns(work_dir=work_dir)
    # get valid new triples
    rate = 0
    if wait_until_file_is_saved(work_dir + "valid_hrt.txt", 120):
        new_hrt_df = read_hrt_2_df(work_dir + "valid_hrt.txt")
        new_hrt_df = pd.concat([new_hrt_df, context_resource.hrt_int_df, context_resource.hrt_int_df]).drop_duplicates(keep=False)
        # add new valid hrt to train set
        old_hrt_df = context_resource.hrt_int_df
        train_hrt_df = pd.concat([old_hrt_df, new_hrt_df], axis=0).drop_duplicates(keep='first')
        # overwrite train data in context
        context_resource.hrt_int_df = train_hrt_df
        # check rate
        new_count = new_hrt_df.count()
        train_count = len(context_resource.hrt_int_df)
        rate = new_count / train_count
    return rate
