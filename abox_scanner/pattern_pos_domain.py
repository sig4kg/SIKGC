import pandas as pd

from abox_scanner.abox_utils import PatternScanner, ContextResources

# domain


class PatternPosDomain(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        def scan_pattern_single_rel(df: pd.DataFrame):
            # for df in aggregated_triples:
            rel = df.iloc[0]['rel']
            if rel in self._pattern_dict:
                correct = self._pattern_dict[rel]
                for idx, row in df.iterrows():
                    h_classes = self._context_resources.entid2classids[row['head']]
                    if not any([h_c in correct for h_c in h_classes]):
                        df.loc[idx, 'correct'] = False
            else:
                df['correct'] = False
            return df
        triples.update(triples.query("correct == True").groupby('rel').apply(lambda x: scan_pattern_single_rel(x)))

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
