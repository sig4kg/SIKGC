from pipelines.pipeline_util import *

def consistency_DBPed():
    triples_path = "../resources/DBpedia-politics/abox_hrt_uri.txt"  # h, t, r
    class_and_op_file_path = "../resources/DBpedia-politics/"
    tbox_patterns_path = "../resources/DBpedia-politics/tbox_patterns"
    wdir = "../outputs/test/"
    context_res = ContextResources(triples_path, class_and_op_file_path=class_and_op_file_path, work_dir=wdir)
    # context_res.hrt_int_df = context_res.hrt_to_scan_df
    abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)
    v, inv = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(wdir, False)
    context_res.hrt_int_df = v
    context_res.to_ntriples(wdir, "../resources/DBpedia-politics/tbox.nt")
    abox_scanner_scheduler.scan_schema_correct_patterns(wdir)


def consistency_NELL():
    triples_path = "../resources/TEST/abox_hrt_uri.txt"  # h, t, r
    class_and_op_file_path = "../resources/NELL/"
    tbox_patterns_path = "../resources/NELL-patterns/"
    wdir = "../outputs/test/"



if __name__ == "__main__":
    consistency_DBPed()




