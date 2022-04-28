from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm


# Irreflexive(r)
class PatternIrreflexive(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        if len(self._pattern_set) == 0:
            return
        # def scan_pattern_single_rel(df: pd.DataFrame):
        #     rel = df.iloc[0]['rel']
        #     if rel in self._pattern_set:
        #         for idx, row in df.iterrows():
        #             h = row['head']
        #             t = row['tail']
        #             if h == t:
        #                 df.loc[idx, 'is_valid'] = False
        #     return df
        # triples.update(triples.query("is_valid == True").groupby('rel').apply(lambda x: scan_pattern_single_rel(x)))
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern Irreflexive"):
            r = g[0]
            if r in self._pattern_set:
                r_triples_df = g[1]
                df.update(r_triples_df.query("head==tail")['is_valid'].apply(lambda x: False))
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_set = set()
            lines = f.readlines()
            for l in lines:
                r = l.strip()[1:-1]
                if r in self._context_resources.op2id:
                    op = self._context_resources.op2id[r]
                    pattern_set.add(op)
            self._pattern_set = pattern_set
