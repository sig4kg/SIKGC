from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import *
from module_utils.blp_util import *
import pandas as pd
from tqdm.auto import trange
from blp.producer import ex
from scripts.run_scripts import clean_blp


def c_l_c(input_hrt_raw_triple_file, work_dir, input_dir, pattern_path, max_epoch=2, inductive=False):
    context_resource = ContextResources(input_hrt_raw_triple_file, work_dir=work_dir, class_and_op_file_path=input_dir, create_id_file=False)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(pattern_path, context_resource)
    # first round scan, get ready for training
    abox_scanner_scheduler.register_pattern([1, 2]).scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(work_dir + "valid_hrt.txt")
    read_scanned_2_context_df(work_dir, context_resource)
    prepare_blp(input_dir, work_dir)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        hrt_int_df_2_hrt_blp(context_resource, work_dir, triples_only=False)    # generate all_triples.tsv, entities.txt, relations.txt\
        wait_until_file_is_saved(work_dir + "all_triples.tsv")
        split_all_triples(work_dir, inductive=inductive) # split all_triples.tsv to train.tsv, dev.tsv, takes time
        wait_until_blp_data_ready(work_dir, inductive=inductive)

        # 1. run blp
        ex.run(config_updates={'work_dir': work_dir,
                               'inductive': inductive,
                               "do_downstream_sample": False,
                               'model': "bert-bow"})
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
        # new_count = len(new_hrt_df)

        # 4. check rate
        # train_count = len(context_resource.hrt_tris_int_df)
        # if new_count / train_count < 0.001:
        #     break

        # 5. add new valid hrt to train data
        extend_hrt_df = pd.concat([context_resource.hrt_int_df, new_hrt_df], axis=0)
        context_resource.hrt_int_df = extend_hrt_df

    hrt_int_df_2_hrt_blp(context_resource, work_dir, triples_only=True)  # generate all_triples.tsv
    wait_until_file_is_saved(work_dir + "all_triples.tsv")


if __name__ == "__main__":
    # df1 = pd.DataFrame(data=[0,1,2])
    # df2 = pd.DataFrame(data=[1,2,3,4,5,6,7])
    # df2notindf1 = pd.concat([df2, df1, df1]).drop_duplicates(keep=False)
    # print("CLC pipeline")
    # c_l_c("../outputs/umls/all_triples.tsv", "../outputs/umls/")
    os.system("rm ../outputs/clc/*")
    # c_l_c("../resources/DBpedia-politics/test_dbpedia.txt",
    #       "../outputs/clc/",
    #       input_dir='../resources/DBpedia-politics/',
    #       pattern_path='../resources/DBpedia-politics/tbox_patterns/', inductive=False)
    c_l_c("../resources/DBpedia-politics/test_dbpedia.txt",
          "../outputs/clc/",
          input_dir='../resources/DBpedia-politics/',
          pattern_path='../resources/DBpedia-politics/tbox_patterns/', inductive=True)






