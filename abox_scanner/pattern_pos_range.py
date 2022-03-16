from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm

#range
class PatternPosRange(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        df.update(df.query("is_valid==False")['correct'].apply(lambda x: False))
        gp = df.query("correct == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern range"):
            rel = g[0]
            r_triples_df = g[1]
            if rel in self._pattern_dict:
                correct = self._pattern_dict[rel]
                for idx, row in r_triples_df.iterrows():
                    h_classes = self._context_resources.entid2classids[row['tail']]
                    if not any([h_c in correct for h_c in h_classes]):
                        r_triples_df.loc[idx, 'correct'] = False
            else:
                r_triples_df['correct'] = False
            df.update(r_triples_df.query("correct==False")['correct'].apply(lambda x: False))
        return df
        # def scan_pattern_single_rel(df: pd.DataFrame):
        #     rel = df.iloc[0]['rel']
        #     if rel in self._pattern_dict:
        #         schema_correct = self._pattern_dict[rel]
        #         for idx, row in df.iterrows():
        #             t_classes = self._context_resources.entid2classids[row['tail']]
        #             if not any([t_c in schema_correct for t_c in t_classes]):
        #                 df.loc[idx, 'correct'] = False
        #     else:
        #         df['correct'] = False
        #     return df
        # triples.update(triples.query("correct == True").groupby('rel').apply(lambda x: scan_pattern_single_rel(x)))

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                op = self._context_resources.op2id[items[0][1:-1]]
                range = [self._context_resources.class2id[ii[1:-1]] for ii in items[1][:-2].split('\"') if
                            ii not in ['owl:Nothing']]
                pattern_dict.update({op: range})
            self._pattern_dict = pattern_dict
