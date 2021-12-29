from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm
# domain


# domain of r1 is disjoint with domain of r2
# D(r1)=C1, D(r2)=C2, C1 disjoint C2, <x r1 e1> <x r2 e2>
class Pattern11(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 11"):
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
                df.update(r1_triples_df.query(f"is_new == True and head in @tmp_list")['is_valid'].apply(lambda x: False))
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                r1 = self._context_resources.op2id[items[0][1:-1]]
                r2_l = items[1].split('@@')
                r2 = [self._context_resources.op2id[rr2[1:-1]] for rr2 in r2_l if rr2[1:-1] in self._context_resources.op2id]
                pattern_dict.update({r1: r2})
            self._pattern_dict = pattern_dict
