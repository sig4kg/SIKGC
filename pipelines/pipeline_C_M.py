from tqdm.auto import trange
from pipeline_util import *


def c_m(work_dir, input_dir, schema_file, tbox_patterns_dir, loops=1, schema_in_nt=''):
    run_scripts.delete_dir(work_dir)
    context_resource, abox_scanner_scheduler = prepare_context(work_dir, input_dir, schema_file,
                                                               tbox_patterns_dir=tbox_patterns_dir)
    get_scores = aggregate_scores()
    scores = []
    for ep in trange(loops, colour="green", position=0, leave=True, desc="Pipeline processing"):
        start_time = datetime.datetime.now()
        init_c1, extend_c1, new_count, new_valid_count, new_correct_count = M_block(context_resource,
                                                                                    abox_scanner_scheduler,
                                                                                    work_dir,
                                                                                    schema_in_nt=schema_in_nt)
        duration = datetime.datetime.now() - start_time
        print(f"Materialisation duration: {str(duration)}")
        scores.append(get_scores(init_c1, extend_c1, new_count, new_valid_count, new_correct_count))
    context_resource.to_ntriples(work_dir)
    return scores


if __name__ == "__main__":
    print("CM pipeline")
    c_m(work_dir="../outputs/cm/",
        input_dir="../resources/TREAT/",
        schema_file='../resources/TREAT/tbox.nt',
        tbox_patterns_dir='../resources/TREAT/tbox_patterns/',
        schema_in_nt='../resources/TREAT/tbox.nt')





