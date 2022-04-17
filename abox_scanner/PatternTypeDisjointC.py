from abox_scanner.ContextResources import ContextResources
import pandas as pd
from tqdm import tqdm


class PatternTypeDisjointC():
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources
    # given new triple (e1 rdf:type C1), and pattern C1 disjointwith C2, sc
    # pattern format: C \t C1@@C2@@C3
    def scan_pattern_df_rel(self, type_triples: pd.DataFrame):
        if len(self._pattern_dict) == 0:
            return
        df = type_triples
        gp = df.query("is_valid == True").groupby('head', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern domain disjointness"):
            e = g[0]
            e_types_df = g[1]
            existing_types = self._context_resources.entid2classids[e]
            need_update = False
            for idx, row in e_types_df.iterrows():
                c = row['tail']
                if c not in self._pattern_dict:
                    continue
                disjoint_c = self._pattern_dict[c]
                if any([existing_c in disjoint_c for existing_c in existing_types]):
                    e_types_df.loc[idx, 'is_valid'] = False
                    need_update = True
            if need_update:
                df.update(e_types_df.query("is_valid == False")['is_valid'])
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
                r1_uri = items[0][1:-1]
                if r1_uri not in self._context_resources.class2id:
                    continue
                r1 = self._context_resources.class2id[r1_uri]
                r2_l = items[1].split('@@')
                r2 = [self._context_resources.class2id[rr2[1:-1]] for rr2 in r2_l if rr2[1:-1] in self._context_resources.class2id]
                if len(r2) > 0:
                    pattern_dict.update({r1: r2})
            self._pattern_dict = pattern_dict