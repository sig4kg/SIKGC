from pipeline_util import *


def e_c(work_dir, input_dir, schema_file, tbox_patterns_dir, max_epoch=1, use_gpu=False):
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file, tbox_patterns_dir=tbox_patterns_dir, consistency_check=False)

    context_2_hrt_transE(work_dir, context_resource)
    train_count = len(context_resource.hrt_int_df.index)
    wait_until_train_pred_data_ready(work_dir)

    # 1.train transE
    train_transe.train(work_dir + "train/", use_gpu=use_gpu)
    wait_until_file_is_saved(work_dir + "checkpoint/transe.ckpt")

    # 2. produce triples
    train_transe.produce(in_path=work_dir + "train/", out_file=work_dir + "transE_raw_hrts.txt", threshold=20, use_gpu=use_gpu)
    wait_until_file_is_saved(work_dir + "transE_raw_hrts.txt", 30)

    # 3. consistency checking for new triples + old triples
    new_hrt_df = read_hrts_2_hrt_df(work_dir + "transE_raw_hrts.txt")
    to_scann_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
    # clean
    run_scripts.clean_tranE(work_dir)
    # check all triples
    context_resource.hrt_int_df = None
    valids, _ = abox_scanner_scheduler.set_triples_to_scan_int_df(to_scann_hrt_df).scan_IJ_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")

    # 4. get valid new triples
    new_hrt_df = valids

    # 5. add new valid hrt to train data
    extend_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0).drop_duplicates(keep='first').reset_index(drop=True)
    new_count = len(extend_hrt_df.index) - train_count
    rate = new_count / train_count
    print("update context data")
    context_resource.hrt_int_df = extend_hrt_df
    context_resource.to_ntriples(work_dir)


if __name__ == "__main__":
    print("EC pipeline")
    e_c(work_dir="../outputs/ec/",
        input_dir="../resources/NELL/",
        schema_file='../resources/NELL/tbox.nt',
        tbox_patterns_dir= '../resources/NELL-patterns/', use_gpu=True)







