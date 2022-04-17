from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm

#range
class PatternNegRange(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        if len(self._pattern_dict) == 0:
            return
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 2"):
            rel = g[0]
            r_triples_df = g[1]
            need_update = False
            if rel in self._pattern_dict:
                invalid = self._pattern_dict[rel]
                for idx, row in r_triples_df.iterrows():
                    h_classes = self._context_resources.entid2classids[row['tail']]
                    if any([h_c in invalid for h_c in h_classes]):
                        r_triples_df.loc[idx, 'is_valid'] = False
                        need_update = True
            if need_update:
                df.update(r_triples_df.query("is_valid == False")['is_valid'])
        return df

        # def scan_pattern_single_rel(df: pd.DataFrame):
        #     rel = df.iloc[0]['rel']
        #     if rel in self._pattern_dict:
        #         invalid = self._pattern_dict[rel]['invalid']
        #         for idx, row in df.iterrows():
        #             t_classes = self._context_resources.entid2classids[row['tail']]
        #             if any([t_c in invalid for t_c in t_classes]):
        #                 df.loc[idx, 'is_valid'] = False
        #     return df
        # triples.update(triples.query("is_valid == True").groupby('rel').apply(lambda x: scan_pattern_single_rel(x)))

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
                op = self._context_resources.op2id[items[0][1:-1]]
                disjoint = [self._context_resources.class2id[ii[1:-1]] for ii in items[1][:-1].split('@@') if
                            ii not in ['owl:Nothing']]
                pattern_dict.update({op: disjoint})
            self._pattern_dict = pattern_dict
