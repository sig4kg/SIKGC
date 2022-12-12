import pandas as pd
import datetime
import file_util
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources
import random
from pipelines.exp_config import *
from pipelines.pipeline_util import *
from pipelines.ProducerBlock import PipelineConfig


def evalACC(in_dir, work_dir, max):
    triples_path = in_dir + "abox_hrt_uri.txt"  # h, t, r
    tbox_patterns_path = in_dir + "tbox_patterns/"
    context_res = ContextResources(triples_path, class_and_op_file_path=in_dir, work_dir=work_dir)
    abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)
    v, _ = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(work_dir, False)
    context_res.hrt_int_df = v
    random_rel = context_res.id2op.keys()
    random_rel = random_rel if len(random_rel) < max else random.sample(random_rel, max)
    random_df = pd.DataFrame(data=random_rel, columns=['rel'])
    candidate_ents = context_res.id2ent.keys()
    random_df['c_h'] = random_df['rel'].apply(
        func=lambda x: random.sample(candidate_ents, max))
    random_df.reset_index(drop=True)
    random_df['c_t'] = random_df['rel'].apply(
        func=lambda x: random.sample(candidate_ents, max))
    random_df.reset_index(drop=True)

    def explode(tmp_df, col, rename_col) -> pd.DataFrame:
        tmp_df[col] = tmp_df[col].apply(lambda x: list(x))
        tm = pd.DataFrame(list(tmp_df[col])).stack().reset_index(level=0)
        tm = tm.rename(columns={0: rename_col}).join(tmp_df, on='level_0'). \
            drop(axis=1, labels=[col, 'level_0']).reset_index(drop=True)
        return tm

    random_df = explode(random_df, "c_h", "head").dropna(how='any')
    random_df = explode(random_df, "c_t", "tail").dropna(how='any').astype('int64')
    random_df = random_df.sample(n=max)[['head', 'rel', 'tail']]
    start_time = datetime.datetime.now()
    to_scan_df = pd.concat([context_res.hrt_int_df, random_df]).drop_duplicates(keep="first").reset_index(
        drop=True)
    context_res.hrt_to_scan_df = to_scan_df
    _, inv = abox_scanner_scheduler.scan_rel_IJPs(work_dir="", save_result=False, log_process=True)
    print(f"The time of ABox scanning is {datetime.datetime.now() - start_time}")
    print(f"inv count:{len(inv.index)}")
    inv = inv[['head', 'rel', 'tail']]
    context_res.hrt_int_df = pd.concat([context_res.hrt_int_df, inv]).drop_duplicates(keep="first").reset_index(
        drop=True)
    context_res.to_ntriples(work_dir=work_dir, schema_in_nt=in_dir + "tbox.nt")
    inv[['head', 'tail']] = inv[['head', 'tail']].applymap(lambda x:  context_res.id2ent[x])
    inv[['rel']] = inv[['rel']].applymap(lambda x: context_res.id2op[x])  # to uri
    inv.to_csv(work_dir + "inv.csv",  header=False, index=False, sep='\t')


if __name__ == "__main__":
    # indir = "../resources/TREAT/"
    # wdir = "../outputs/test/"
    # indir = "../resources/NELL/"
    # wdir = "../outputs/test/"
    indir = "../resources/DBpedia-politics/"
    wdir = "../outputs/test/"
    evalACC(indir, wdir, 100)

