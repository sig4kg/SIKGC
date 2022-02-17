from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd

#range
class PatternPosRange(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        def scan_pattern_single_rel(df: pd.DataFrame):
            rel = df.iloc[0]['rel']
            if rel in self._pattern_dict:
                schema_correct = self._pattern_dict[rel]
                for idx, row in df.iterrows():
                    t_classes = self._context_resources.entid2classids[row['tail']]
                    if not any([t_c in schema_correct for t_c in t_classes]):
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
                range = [self._context_resources.class2id[ii[1:-1]] for ii in items[1][:-2].split('\"') if
                            ii not in ['owl:Nothing']]
                pattern_dict.update({op: range})
            self._pattern_dict = pattern_dict
