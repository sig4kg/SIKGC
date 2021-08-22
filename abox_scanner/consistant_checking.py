from abox_scanner import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources


if __name__ == "__main__":
    # triples_path = "../resources/NELL-995/NELLKG0.txt"  # h, t, r
    # tbox_patterns_path = "../resources/NELL_patterns"
    # context_res = ContextResources(triples_path, work_dir="outputs/test/")
    #
    # # pattern_input_dir, class2int, node2class_int, all_triples_int
    # abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)
    #
    # abox_scanner_scheduler.register_pattern([1])
    # abox_scanner_scheduler.scan_patterns(work_dir='../outputs/test/')

    triples_path = "../resources/DBpedia-politics/PoliticalTriplesWD.txt"  # h, t, r
    tbox_patterns_path = "../resources/DBpedia-politics/tbox-dbpedia/"
    context_res = ContextResources(triples_path, class_and_op_file_path= tbox_patterns_path, work_dir="../outputs/test/", create_id_file=True)

    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)

    abox_scanner_scheduler.register_pattern([1])
    abox_scanner_scheduler.scan_patterns(work_dir='../outputs/test/')








