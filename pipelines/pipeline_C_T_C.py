from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from openKE import train_transe_NELL995
import pandas as pd

ONTOLOGY_PATH = "../resources/NELL.ontology.ttl"
TBOX_PATTERNS_PATH = "../resources/NELL_patterns"
ALL_CLASS_PATH = "../resources/NELL-995/ALLClasses.txt"
ORIGINAL_TRIPLES_PATH = "../resources/NELL-995/NELLKG0.txt"


class ContextResources:
    def __init__(self, original_hrt_triple_file_path, output_dir):
         # h, r, t
        all_triples = abox_utils.read_all_triples(original_hrt_triple_file_path)
        self.node2id, self.original_tris_int = abox_utils.hrt_triples2int(all_triples, f"{output_dir}/train/")
        self.class2id = abox_utils.class2int(ALL_CLASS_PATH, self.node2id)
        self.nodeid2classid = abox_utils.nodeid2classid_nell(self.node2id, self.class2id)


def c_t_c(input_hrt_triple_file, output_dir, max_epoch=5):
    context_resource = ContextResources(input_hrt_triple_file)
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler(TBOX_PATTERNS_PATH,
                                                  context_resource.class2id,
                                                  context_resource.nodeid2classid,
                                                  context_resource.original_tris_int)
    abox_scanner_scheduler.register_pattern([1, 2])
    # first round scan, get ready for training
    abox_scanner_scheduler.scan_patterns(output_dir=output_dir)
    abox_utils.hrt2rht_transE(output_dir + "valid_hrt.txt", output_dir + "/train/train2id.txt")

    for ep in range(max_epoch):
        # train transE
        train_transe_NELL995.train(output_dir + "/train")
        # produce triples
        train_transe_NELL995.produce(output_dir + "/train", output_dir + "transE_raw_hrt.txt")
        train_count, old_hrt_df = abox_utils.read_htr_train_2_hrt_df(output_dir + "/train/train2id.txt")
        # consistency checking for new triples
        new_hrt_df = abox_utils.read_hrts_2_df(output_dir + "transE_raw_hrt.txt")
        abox_scanner_scheduler._all_triples_int = new_hrt_df.values.tolist()
        abox_scanner_scheduler.scan_patterns(output_dir=output_dir)
        # get valid new triples
        new_hrt_df = abox_utils.read_hrt_2_df(output_dir + "valid_hrt.txt")
        new_count = new_hrt_df.count()
        # check rate
        if new_count / train_count < 0.001:
            break
        # add new valid to train set
        train_hrt_df = pd.concat([old_hrt_df, new_hrt_df], axis=0)
        # create train data
        abox_utils.hrt_df2htr_transE(train_hrt_df, output_dir + "/train/train2id.txt")



