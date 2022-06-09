import pandas as pd
from tqdm import tqdm

from abox_scanner.ContextResources import PatternScanner, ContextResources

# domain


class PatternNegDomain(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame, log_process=True):
        if len(self._pattern_dict) == 0:
            return
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern domain disjointness", disable=not log_process):
            rel = g[0]
            r_triples_df = g[1]
            need_update = False
            if rel in self._pattern_dict:
                invalid = self._pattern_dict[rel]
                for idx, row in r_triples_df.iterrows():
                    h_classes = self._context_resources.entid2classids[row['head']]
                    if any([h_c in invalid for h_c in h_classes]):
                        r_triples_df.loc[idx, 'is_valid'] = False
                        need_update = True
            if need_update:
                df.update(r_triples_df.query("is_valid == False")['is_valid'])
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
                op = self._context_resources.op2id[items[0][1:-1]]
                disjoint = [self._context_resources.class2id[ii[1:-1]] for ii in items[1].split('@@') if ii not in ['owl:Nothing']]
                pattern_dict.update({op: disjoint})
            self._pattern_dict = pattern_dict
