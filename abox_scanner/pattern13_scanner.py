from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm


# FunctionalProperty(r2), Inverseof(r1, r2) ---- <y r1 x> <z r1 x> and <x r2 y> <z r1 x>
class Pattern13(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 13"):
            r = g[0]
            if r in self._pattern_set:
                r_triples_df = g[1]
                # have defect as we should restrict y != z
                # heads = r_triples_df['head'].to_list()
                # tails = r_triples_df['tail'].to_list()
                # df.update(r_triples_df.query(f"tail in @heads and head!= and is_new==True")['is_valid'].apply(lambda x: False))
                # df.update(r_triples_df.query(f"head in @tails and is_new==True")['is_valid'].apply(lambda x: False))
                # keep=False : Mark all duplicates as True.
                df.update(r_triples_df[r_triples_df.duplicated('tail', keep=False)].
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
