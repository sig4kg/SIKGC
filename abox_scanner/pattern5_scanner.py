from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm


# asymmetric
class Pattern5(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 5"):
            r = g[0]
            if r in self._pattern_set:
                r_triples_df = g[1]
                # very slow
                # for idx, row in tqdm(df.iterrows()):
                #     h = row['head']
                #     t = row['tail']
                #     r_triples_df.update(r_triples_df.query("head == @t and tail == @h")['is_valid'].apply(lambda x: False))
                switch_ht_df = pd.DataFrame({'head': r_triples_df['tail'].values, 'tail': r_triples_df['head'].values})
                not_duplicated_items = pd.concat([r_triples_df[['head', 'tail']], switch_ht_df, switch_ht_df]).drop_duplicates(keep=False)
                duplicated_items = pd.concat([r_triples_df[['head', 'tail']], not_duplicated_items]).drop_duplicates(keep=False)
                df.update(r_triples_df[r_triples_df.index.isin(duplicated_items.index)].query("is_new==True")['is_valid'].apply(lambda x: False))
        return df

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
