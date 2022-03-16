import pandas as pd

from abox_scanner.ContextResources import PatternScanner, ContextResources
from tqdm import tqdm
# domain


class PatternGenSymetric(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = set()
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        gp = triples.groupby('rel', group_keys=True, as_index=False)
        new_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        for g in tqdm(gp, desc="scanning pattern generator reflexive"):
            rel = g[0]
            r_triples_df = g[1]
            if rel in self._pattern_set:
                tmp_df = r_triples_df[['tail', 'rel', 'head']]
                new_df = pd.concat([new_df, tmp_df]).drop_duplicates(keep='first')
        new_df = new_df.drop_duplicates(keep='first')
        new_df = pd.concat([new_df, triples, triples]).drop_duplicates(keep=False).reset_index()
        return new_df


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
