from abox_scanner import abox_utils
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.abox_utils import read_scanned_2_context_df, wait_until_file_is_saved, ContextResources
from scripts import run_scripts
from tqdm.auto import trange
from module_utils.materialize_util import *


def c_m(input_hrt_triple_file, work_dir, class_op_and_pattern_path, schema_file, max_epoch=2, dataset='nell'):
    context_resource = ContextResources(input_hrt_triple_file,
                                        work_dir=work_dir,
                                        class_and_op_file_path=class_op_and_pattern_path,
                                        create_id_file=False,
                                        dataset=dataset)
    run_scripts.clean_materialization(work_dir=work_dir)
    abox_scanner_scheduler = AboxScannerScheduler(class_op_and_pattern_path, context_resource)
    abox_scanner_scheduler.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13])
    # first round scan, get ready for training
    abox_scanner_scheduler.scan_patterns(work_dir=work_dir)
    wait_until_file_is_saved(f"{work_dir}valid_hrt.txt", 60)
    read_scanned_2_context_df(work_dir, context_resource)
    preparing_tbox_to_dllite(schema_file, work_dir)
    for ep in trange(max_epoch, colour="green", position=0, leave=True, desc="Pipeline processing"):
        # context int to materialization ntriples,
        hrt_int_df_2_hrt_ntriples(context_resource, work_dir)
        wait_until_file_is_saved(work_dir + "abox.nt", 120)

        # the result is materialized_abox.nt
        print("running materialization...")
        materialize(work_dir)

        # read new data to context
        # we only keep entities in original abox. If node absent from original abox, we delete them.
        materialized_hrt_int_df = nt_2_hrt_int_df(work_dir + "cleaned_tbox_abox.nt", context_resource)
        context_resource.hrt_int_df = pd.concat([context_resource.hrt_int_df, materialized_hrt_int_df]).drop_duplicates(keep='first')
        #  backup and clean last round data
        run_scripts.clean_materialization(work_dir=work_dir)

    hrt_int_df_2_hrt_ntriples(context_resource, work_dir)


if __name__ == "__main__":
    print("CM pipeline")
    c_m(input_hrt_triple_file="../resources/NELL/abox_hrt_uri.txt",
        work_dir="../outputs/cm/",
        class_op_and_pattern_path='../resources/NELL-patterns/',
        schema_file='../resources/NELL/NELL.ontology.nt',
        dataset='nell')
    # c_m(input_hrt_triple_file="../resources/DBpedia-politics/PoliticalTriplesWD.txt",
    #     work_dir="../outputs/cm/",
    #     class_op_and_pattern_path='../resources/DBpedia-politics/tbox-dbpedia/',
    #     schema_file="../resources/DBpedia-politics/dbpedia_2016-10.owl")





