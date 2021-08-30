from abox_scanner.abox_utils import PatternScanner, ContextResources

# domain


class Pattern1(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, aggregated_triples):
        # for df in aggregated_triples:
        df = aggregated_triples
        rel = df.iloc[0]['rel']
        if rel in self._pattern_dict:
            invalid = self._pattern_dict[rel]['invalid']
            for idx, row in df.iterrows():
                h_classes = self._context_resources.entid2classids[row['head']]
                if any([h_c in invalid for h_c in h_classes]):
                    df.loc[idx, 'is_valid'] = False
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            if self._context_resources.dataset_name != 'dbpedia':
                for l in lines:
                    items = l.split('\t')
                    op = self._context_resources.op2id[items[0][1:-1].split('/')[-1]]
                    ont2 = self._context_resources.class2id[items[1][1:-1].split('/')[-1]]
                    disjoint = [self._context_resources.class2id[ii[1:-1].split('/')[-1]] for ii in items[2][:-2].split('\"') if ii not in ['owl:Nothing']]
                    pattern_dict.update({op: {'valid': ont2, 'invalid': disjoint}})
            else:
                for l in lines:
                    items = l.split('\t')
                    op = self._context_resources.op2id[items[0][1:-1]]
                    ont2 = self._context_resources.class2id[items[1][1:-1]]
                    disjoint = [self._context_resources.class2id[ii[1:-1]] for ii in items[2][:-2].split('\"') if ii not in ['owl:Nothing']]
                    pattern_dict.update({op: {'valid': ont2, 'invalid': disjoint}})
            self._pattern_dict = pattern_dict
