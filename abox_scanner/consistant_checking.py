import pandas as pd
from pipelines.pipeline_util import *
from abox_scanner.pattern_type_scanner import PatternTypeDiscjointness

if __name__ == "__main__":
    # triples_path = "../resources/DBpedia-politics/abox_hrt_uri.txt"  # h, t, r
    # class_and_op_file_path = "../resources/DBpedia-politics/"
    # tbox_patterns_path = "../resources/DBpedia-politics/tbox_patterns"
    triples_path = "../resources/TEST/abox_hrt_uri.txt"  # h, t, r
    class_and_op_file_path = "../resources/NELL/"
    tbox_patterns_path = "../resources/NELL-patterns/"
    wdir = "../outputs/test/"


    context_res = ContextResources(triples_path, class_and_op_file_path= class_and_op_file_path, work_dir=wdir, create_id_file=False)
    context_res.hrt_int_df = context_res.hrt_to_scan_df
    context_res.to_ntriples(work_dir=wdir, schema_in_nt=class_and_op_file_path + "tbox.nt")
    # fix_type = PatternTypeDiscjointness(context_res)
    # fix_type.pattern_to_int("../resources/DBpedia-politics/TBoxPattern_class_disjointness.txt")
    # fix_type.scan_pattern_df_rel("../outputs/test/")
    # context_res.type_ntriples(work_dir=wdir, schema_in_nt='../resources/DBpedia-politics/tbox.nt')
    # pattern_input_dir, class2int, node2class_int, all_triples_int
    # abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)
    # context_res.hrt_int_df = context_res.hrt_to_scan_df
    # abox_scanner_scheduler.register_gen_pattern()
    # t = abox_scanner_scheduler.scan_generator_patterns()
    # abox_scanner_scheduler.register_pattern([1, 2, 5,8,9,10,11,12,13], ['pos_domain', 'pos_range'])
    # valids, invalids = abox_scanner_scheduler.scan_IJ_patterns(work_dir='../outputs/test/')

    # abox_scanner_scheduler.scan_schema_correct_patterns(work_dir='../outputs/test/')
    # context_res.hrt_int_df = valids
    # to_ntriples(context_res, wdir)








