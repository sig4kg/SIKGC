import pandas as pd

from pipelines.M import M
from pipelines.ProducerBlock import PipelineConfig
from pipelines.exp_config import DatasetConfig
from module_utils.sample_util import *
# dev + materialised triples
from pipelines.pipeline_util import prepare_context


def get_schema_aware_silver_testset(dataset="TEST", out_dir="./", exclude_rels=[], exclude_ents=[]):
    d_conf = DatasetConfig().get_config(dataset='TEST')
    p_config = PipelineConfig()
    p_config.set_config(blp_config={},
                        data_config=d_conf,
                        dataset=dataset,
                        loops=1,
                        work_dir=out_dir,
                        use_gpu=False)
    context_resource, abox_scanner_scheduler = prepare_context(p_config, consistency_check=True)
    old_rel_ax = context_resource.hrt_int_df.copy(deep=True)
    old_type_ax = context_resource.type2hrt_int_df().copy(deep=True)
    df_rel_train, df_rel_dev, df_rel_test = split_relation_triples(context_resource=context_resource,
                                                                   exclude_rels=exclude_rels,
                                                                   produce=False)
    df_type_train, df_type_dev, df_type_test = split_type_triples(context_resource=context_resource,
                                                                  exclude_ents=exclude_ents,
                                                                  produce=False)
    materialisation = M((context_resource, abox_scanner_scheduler, p_config))
    materialisation.produce()
    extended_rel_ax = context_resource.hrt_int_df
    extended_type_ax = context_resource.type2hrt_int_df()
    new_rel_test = pd.concat(extended_rel_ax, old_rel_ax, old_rel_ax).drop_duplicates(keep=False)
    new_type_test = pd.concat(extended_type_ax, old_type_ax, old_type_ax).drop_duplicates(keep=False)
    schema_aware_silver_test_rel_ax = pd.concat(df_rel_test, new_rel_test).reset_index(drop=True)
    schema_aware_silver_test_type_ax = pd.concat(df_type_test, new_type_test).reset_index(drop=True)
    return schema_aware_silver_test_rel_ax, schema_aware_silver_test_type_ax