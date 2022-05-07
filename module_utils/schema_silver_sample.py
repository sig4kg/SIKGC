from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from pipelines.M import M
from pipelines.ProducerBlock import PipelineConfig
from pipelines.exp_config import DatasetConfig
from module_utils.sample_util import *
from pipelines.pipeline_util import prepare_context


# dev + materialised triples
def get_schema_aware_silver_testset(p_config: PipelineConfig,
                                    context_resource: ContextResources,
                                    exclude_rels=[],
                                    exclude_ents=[],
                                    produce=True):
    old_rel_ax = context_resource.hrt_int_df.copy(deep=True)
    old_type_ax = context_resource.type2hrt_int_df().copy(deep=True)
    df_rel_train, df_rel_dev, df_rel_test = split_relation_triples(context_resource=context_resource,
                                                                   exclude_rels=exclude_rels,
                                                                   produce=produce)
    dict_type_train, dict_type_dev, dict_type_test = split_type_triples(context_resource=context_resource,
                                                                  exclude_ents=exclude_ents,
                                                                  produce=produce)
    materialisation = M(context_resource, p_config)
    materialisation.produce()
    extended_rel_ax = context_resource.hrt_int_df
    extended_type_ax = context_resource.type2hrt_int_df()
    new_rel_test = pd.concat([extended_rel_ax, old_rel_ax, old_rel_ax]).drop_duplicates(keep=False)
    new_type_test = pd.concat([extended_type_ax, old_type_ax, old_type_ax]).drop_duplicates(keep=False)
    schema_aware_silver_test_rel_ax = pd.concat([df_rel_dev, new_rel_test]).reset_index(drop=True)

    schema_aware_silver_test_type_ax = pd.concat([df_type_dev, new_type_test]).reset_index(drop=True)
    samples = {
        "rel_train": df_rel_train,
        "rel_dev": df_rel_dev,
        "rel_test": df_rel_test,
        "rel_silver": schema_aware_silver_test_rel_ax,
        "type_train": df_type_train,
        "type_dev": df_type_dev,
        "type_test": df_type_test,
        "type_silver": schema_aware_silver_test_type_ax
    }
    return samples


def get_schema_aware_silver_testset_from_start(dataset="TEST",
                                               out_dir="./",
                                               exclude_rels=[],
                                               exclude_ents=[],
                                               produce=True):
    d_conf = DatasetConfig().get_config(dataset='TEST')
    p_config = PipelineConfig()
    p_config.set_pipeline_config(blp_config={},
                                 data_config=d_conf,
                                 dataset=dataset,
                                 loops=1,
                                 work_dir=out_dir,
                                 use_gpu=False)
    context_resource, abox_scanner_scheduler = prepare_context(p_config, consistency_check=True)
    return get_schema_aware_silver_testset(p_config,
                                           context_resource,
                                           abox_scanner_scheduler,
                                           exclude_rels=exclude_rels,
                                           exclude_ents=exclude_ents,
                                           produce=produce)