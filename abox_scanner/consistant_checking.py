import pandas as pd

from abox_scanner import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources


if __name__ == "__main__":
    # triples_path = "../resources/DBpedia-politics/test_dbpedia.txt"  # h, t, r
    triples_path = "../resources/NELL/abox_hrt_uri.txt"  # h, t, r
    class_and_op_file_path = "../resources/NELL/"
    tbox_patterns_path = "../resources/NELL-patterns/"

    # triples_path = "../resources/DBpedia-politics/PoliticalTriplesWD.txt"  # h, t, r
    # class_and_op_file_path = "../resources/DBpedia-politics/"
    # tbox_patterns_path = "../resources/DBpedia-politics/tbox_patterns/"

    context_res = ContextResources(triples_path, class_and_op_file_path= class_and_op_file_path, work_dir="../outputs/test/", create_id_file=True)

    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)

    abox_scanner_scheduler.register_pattern([5,8,9,10,11,12,13], ['pos_domain', 'pos_range'])
    abox_scanner_scheduler.scan_IJ_patterns(work_dir='../outputs/test/')
    abox_scanner_scheduler.scan_schema_correct_patterns(work_dir='../outputs/test/')








