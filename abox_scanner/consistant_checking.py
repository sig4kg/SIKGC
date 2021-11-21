import pandas as pd

from abox_scanner import AboxScannerScheduler
from abox_scanner.abox_utils import ContextResources


if __name__ == "__main__":
    df1 = pd.DataFrame({'Animal': ['Falcon', 'Falcon',
                                  'Parrot', 'Parrot'],
                       'test': ['F', 'p',
                                  'P', 'P'],
                       'Max Speed': [380., 370., 24., 26.]})
    df2 = pd.DataFrame({'Animal': ['Falcon', 'Falcon',
                                  'Parrot', 'Parrot', 'new'],
                        'test': ['F', 'p',
                                 'P', 'P', 'new'],
                        'Max Speed': [380., 370., 24., 26., 0]})
    new_items = pd.concat([df1, df2]).drop_duplicates(keep=False)
    df2['is_new'] = True
    # df2.update(df2[(df2.Animal.isin(new_items['Animal'])) & df2.test.isin(new_items['test'])]['is_new'].apply(lambda x: False))
    df1.update(df1[df1.duplicated('Animal', keep=False)]['Max Speed'].apply(lambda x: 0))
    print(df1)

    # triples_path = "../resources/DBpedia-politics/test_dbpedia.txt"  # h, t, r
    triples_path = "../resources/DBpedia-politics/PoliticalTriplesWD.txt"  # h, t, r
    tbox_patterns_path = "../resources/DBpedia-politics/tbox-dbpedia/"
    context_res = ContextResources(triples_path, class_and_op_file_path= tbox_patterns_path, work_dir="../outputs/test_dbpedia/", create_id_file=True)

    # pattern_input_dir, class2int, node2class_int, all_triples_int
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)

    abox_scanner_scheduler.register_pattern([1, 2, 9, 10, 11])
    abox_scanner_scheduler.scan_patterns(work_dir='../outputs/test_dbpedia/')








