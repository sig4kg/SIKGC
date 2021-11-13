from abox_scanner.abox_utils import PatternScanner, ContextResources


# Irreflexive(r)
class Pattern8(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, aggregated_triples):
        df = aggregated_triples
        rel = df.iloc[0]['rel']
        if rel in self._pattern_set:
            for idx, row in df.iterrows():
                h = row['head']
                t = row['tail']
                if h == t:
                    df.loc[idx, 'is_valid'] = False
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_set = set()
            lines = f.readlines()
            if self._context_resources.dataset_name != 'dbpedia':
                for l in lines:
                    items = l.split('\t')
                    rel = self._context_resources.op2id[items[0][1:][:-1].split('/')[-1]]
                    pattern_set.add(rel)
            else:
                for l in lines:
                    items = l.split('\t')
                    op = self._context_resources.op2id[items[0][1:-1]]
                    pattern_set.add(op)
            self._pattern_set = pattern_set
