import pandas as pd

from abox_scanner.ContextResources import PatternScanner, ContextResources
from tqdm import tqdm
# domain


class PatternGenSubproperty(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.groupby('rel', group_keys=True, as_index=False)
        new_df = pd.DataFrame(data=[], columns=['head', 'rel','tail'])
        for g in tqdm(gp, desc="scanning pattern generator for inverse property"):
            rel = g[0]
            r_triples_df = g[1]
            if rel in self._pattern_dict:
                inverse_of_r = self._pattern_dict[rel]
                for r_inv in inverse_of_r:
                    tmp_df = r_triples_df[['head', 'rel', 'tail']]
                    tmp_df['rel'] = r_inv
                new_df = pd.concat([new_df, tmp_df]).drop_duplicates(keep='first')
        new_df = new_df.drop_duplicates(keep='first')
        new_df = pd.concat([new_df, triples, triples]).drop_duplicates(keep=False).reset_index()
        return new_df


    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                r1 = self._context_resources.op2id[items[0][1:-1]]
                if r1 not in self._context_resources.op2id:
                    continue
                r2_l = items[1].split('@@')
                r2 = [self._context_resources.op2id[rr2[1:-1]] for rr2 in r2_l if rr2[1:-1] in self._context_resources.op2id]
                if len(r2) > 0:
                    pattern_dict.update({r1: r2})
            self._pattern_dict = pattern_dict
