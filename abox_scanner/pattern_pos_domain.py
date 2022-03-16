import pandas as pd

from abox_scanner.ContextResources import PatternScanner, ContextResources
from tqdm import tqdm
# domain


class PatternPosDomain(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        df.update(df.query("is_valid==False")['correct'].apply(lambda x: False))
        gp = df.query("correct==True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern domain"):
            rel = g[0]
            r_triples_df = g[1]
            if rel in self._pattern_dict:
                correct = self._pattern_dict[rel]
                for idx, row in r_triples_df.iterrows():
                    h_classes = self._context_resources.entid2classids[row['head']]
                    if not any([h_c in correct for h_c in h_classes]):
                        r_triples_df.loc[idx, 'correct'] = False
            else:
                r_triples_df['correct'] = False
            df.update(r_triples_df.query("correct==False")['correct'].apply(lambda x: False))
        return df


    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                op = self._context_resources.op2id[items[0][1:-1]]
                domain = [self._context_resources.class2id[ii[1:-1]] for ii in items[1][:-2].split('\"') if ii not in ['owl:Nothing']]
                pattern_dict.update({op: domain})
            self._pattern_dict = pattern_dict
