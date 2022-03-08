from abox_scanner.abox_utils import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm
import torch


# FunctionalProperty(r1), Inverseof(r1, r2) ---- <y r2 x> <z r2 x> and <x r1 y> <z r2 x>
# r1    r2@@r3@@r4
class Pattern13(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = dict()
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        if torch.cuda.is_available():
            import cudf
            df = cudf.DataFrame.from_pandas(triples)
        else:
            df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern 13"):
            r1 = g[0]
            if r1 in self._pattern_dict:
                r2_l = list(set(self._pattern_dict[r1]))
                r1_df = g[1]
                # have defect as we should restrict y != z
                # heads = r_triples_df['head'].to_list()
                # tails = r_triples_df['tail'].to_list()
                # df.update(r_triples_df.query(f"tail in @heads and head!= and is_new==True")['is_valid'].apply(lambda x: False))
                # df.update(r_triples_df.query(f"head in @tails and is_new==True")['is_valid'].apply(lambda x: False))
                # keep=False : Mark all duplicates as True.
                for r2 in r2_l:
                    if r1 == r2:
                        # <y r x> <z r x>
                        df.update(r1_df[r1_df.duplicated('tail', keep=False)].
                                  query("is_new==True")['is_valid'].apply(lambda x: False))
                        # <x r y> <z r x>
                        for idx, row in r1_df.iterrows():
                            x = row['head']
                            y = row['tail']
                            df.update(r1_df.query("head != @y and tail == @x and is_new==True")['is_valid'].apply(lambda x: False))
                    else:
                        if r2 not in gp.groups:
                            continue
                        r2_df = gp.get_group(r2)
                        # <y r2 x> <z r2 x>
                        df.update(r2_df[r2_df.duplicated('tail', keep=False)].
                                  query("is_new==True")['is_valid'].apply(lambda x: False))
                        # <x r1 y> <z r2 x>
                        for idx, row in r1_df.iterrows():
                            x = row['head']
                            y = row['tail']
                            df.update(r2_df.query("head != @y and tail == @x and is_new==True")['is_valid'].apply(lambda x: False))
        if torch.cuda.is_available():
            df = df.head().to_pandas()
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                r1 = items[0].strip()[1:-1]
                if r1 in self._context_resources.op2id:
                    op = self._context_resources.op2id[r1]
                    r2_l = items[1].strip().split("@@")
                    op2_l = []
                    for r2 in r2_l:
                        if r2[1:-1] in self._context_resources.op2id:
                            op2 = self._context_resources.op2id[r2[1:-1]]
                            op2_l.append(op2)
                    op2_l = list(set(op2_l))
                    if len(op2_l) > 0:
                        self._pattern_dict.update({op: op2_l})
