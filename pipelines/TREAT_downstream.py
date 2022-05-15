from pipelines.exp_config import *
from pipeline_util import *
from pipelines.ProducerBlock import PipelineConfig
from module_utils.blp_util import *
import pandas as pd
from blp.producer import ex


def TREAT_for_downstream_task(work_dir):
    dataset = "TREAT"
    data_conf = DatasetConfig().get_config(dataset)
    blp_conf = BLPConfig().get_blp_config(rel_model="transe", inductive=False, dataset=dataset, schema_aware=True)
    p_config = PipelineConfig().set_pipeline_config(dataset=dataset,
                                                    loops=1,
                                                    work_dir=work_dir,
                                                    pred_type=False,
                                                    reasoner=None,
                                                    parallel=False,
                                                    pipeline='l',
                                                    silver_eval=False,
                                                    use_gpu=True)
    p_config.set_blp_config(blp_conf).set_data_config(data_conf)
    context_resource, abox_scanner_scheduler = prepare_context(p_config, consistency_check=True)

    hrt_int_df_2_hrt_blp(context_resource, work_dir,
                         triples_only=False)  # generate all_triples.tsv, entities.txt, relations.txt\
    wait_until_file_is_saved(work_dir + "all_triples.tsv")
    split_data_blp(context_resource=context_resource, work_dir=work_dir, inductive=False,
                      exclude_rels=[])  # split all_triples.tsv to train.tsv, dev.tsv, takes time
    wait_until_blp_data_ready(work_dir, inductive=False)
    # 1. run blp
    p_config.blp_config.update({'work_dir': work_dir, 'do_downstream_sample': True, 'do_produce': True})
    ex.run(config_updates=p_config.blp_config)
    wait_until_file_is_saved(work_dir + "blp_new_triples.csv", 60 * 3)

    # 2. consistency checking for new triples
    pred_hrt_df = read_hrts_blp_2_hrt_int_df(work_dir + "blp_new_triples.csv", context_resource).drop_duplicates(
        keep='first').reset_index(drop=True)
    print("all produced triples: " + str(len(pred_hrt_df.index)))

    # 3. get valid new triples
    to_scan_df = pd.concat([context_resource.hrt_int_df, pred_hrt_df]).drop_duplicates(keep="first").reset_index(
        drop=True)
    abox_scanner_scheduler.set_triples_to_scan_int_df(to_scan_df).scan_rel_IJPs(work_dir=work_dir, save_result=True)


if __name__ == "__main__":
    TREAT_for_downstream_task("../outputs/treat_downstream/")
