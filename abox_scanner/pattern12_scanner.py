from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm


# FunctionalProperty(r) ----- <x r y> <x r z>
class Pattern12(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 12"):
            r = g[0]
            if r in self._pattern_set:
                r_triples_df = g[1]
                df.update(r_triples_df[r_triples_df.duplicated('head', keep=False)].
                                    query("is_new==True")['is_valid'].apply(lambda x: False))
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_set = set()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                r = items[0].strip()[1:-1]
                if r in self._context_resources.op2id:
                    op = self._context_resources.op2id[r]
                    pattern_set.add(op)
            self._pattern_set = pattern_set
