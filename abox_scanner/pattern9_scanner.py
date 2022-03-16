from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm
# domain

# range of r1 is disjoint with domain of r2
# R(r1)=C1, D(r2)=C2, C1 disjoint C2, <e1 r1 x> <x r2 e2>
class Pattern9(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 9"):
            r1 = g[0]
            if r1 in self._pattern_dict:
                disjoint_r2_l = self._pattern_dict[r1]
                r1_triples_df = g[1]
                tmp_list = []
                for r2 in disjoint_r2_l:
                    if r2 not in gp.groups:
                        continue
                    r2_triples_df = gp.get_group(r2)
                    r2_head = r2_triples_df['head'].to_list()
                    tmp_list.extend(r2_head)
                df.update(r1_triples_df.query(f"tail in @tmp_list and is_new==True")['is_valid'].apply(lambda x: False))
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
                r1_uri = items[0][1:-1]
                if r1_uri not in self._context_resources.op2id:
                    continue
                r1 = self._context_resources.op2id[r1_uri]
                r2_l = items[1].split('@@')
                r2 = [self._context_resources.op2id[rr2[1:-1]] for rr2 in r2_l if rr2[1:-1] in self._context_resources.op2id]
                if len(r2) > 0:
                    pattern_dict.update({r1: r2})
            self._pattern_dict = pattern_dict
