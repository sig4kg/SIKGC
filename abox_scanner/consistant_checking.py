import pandas as pd
from abox_scanner import abox_utils, AboxScannerScheduler


def test(t):
    # for idx, row in t.iterrows():
    t['t'] = 2
    return t

if __name__ == "__main__":
    triples_path = "../resources/NELL-995/NELLKG0.txt"  # h, t, r
    ontology_path = "../resources/NELL.ontology.ttl"
    tbox_patterns_path = "../resources/NELL_patterns"
    all_class_path = "../resources/NELL-995/ALLClasses.txt"

    all_triples = abox_utils.read_all_triples(triples_path)
    node2id, tris_int = abox_utils.hrt_triples2int(all_triples, "../outputs/NELL")
    class2id = abox_utils.class2int(all_class_path, node2id)
    nodeid2classid = abox_utils.nodeid2classid_nell(node2id, class2id)

    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, class2id, nodeid2classid, tris_int)
    abox_scanner_scheduler.register_pattern([1])
    abox_scanner_scheduler.scan_patterns(output_dir='../outputs/')


    # df = pd.DataFrame([1,1,1,0,0,1], columns=['t'])
    # ddf = df.query("t==0")
    # ddff = ddf.groupby("t").apply(test)
    # print("done")








