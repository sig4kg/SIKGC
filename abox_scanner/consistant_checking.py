import pandas as pd

from abox_scanner import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources


if __name__ == "__main__":
    # df = pd.DataFrame({'Animal': ['Falcon', 'Falcon',
    #                               'Parrot', 'Parrot'],
    #                    'test': ['F', 'p',
    #                               'P', 'P'],
    #                    'Max Speed': [380., 370., 24., 26.]})
    # gp = df.groupby(['Animal', 'test'], group_keys=True, as_index=False)
    # for g in gp:
    #     t = g

    # triples_path = "../resources/DBpedia-politics/test_dbpedia.txt"  # h, t, r
    triples_path = "../resources/DBpedia-politics/PoliticalTriplesWD.txt"  # h, t, r
    tbox_patterns_path = "../resources/DBpedia-politics/tbox-dbpedia/"
    context_res = ContextResources(triples_path, class_and_op_file_path= tbox_patterns_path, work_dir="../outputs/test_dbpedia/", create_id_file=True)

    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)

    abox_scanner_scheduler.register_pattern([1, 2, 9, 10, 11])
    abox_scanner_scheduler.scan_patterns(work_dir='../outputs/test_dbpedia/')








