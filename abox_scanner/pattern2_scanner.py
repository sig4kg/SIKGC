from abox_scanner.abox_utils import PatternScanner, ContextResources


#range
class Pattern2(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, aggregated_triples):
        df = aggregated_triples
        rel = df.iloc[0]['rel']
        if rel not in self._pattern_dict:
            return
        else:
            invalid = self._pattern_dict[rel]['invalid']
            for idx, row in df.iterrows():
                if self._context_resources.entid2classid[row['tail']] in invalid:
                    df.loc[idx, 'is_valid'] = False
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                rel = self._context_resources.rel2id[items[0][1:][:-1].split('/')[-1]]
                ont2 = self._context_resources.class2id[items[1][1:][:-1].split('/')[-1]]
                disjoint = [self._context_resources.class2id[ii[1:][:-1].split('/')[-1]] for ii in items[2][:-2].split('\"') if ii not in ['owl:Nothing']]
                pattern_dict.update({rel: {'valid': ont2, 'invalid': disjoint}})
            self._pattern_dict = pattern_dict
