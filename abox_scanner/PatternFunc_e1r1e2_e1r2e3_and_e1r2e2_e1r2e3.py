from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm
import torch


# FunctionalProperty(r1), subPropertyOf(r2, r1) ---- (<e1 r2 e2> <e1 r2 e3> or <e1 r1 e2> <e1 r2 e3> ) and e2 != e3
# r1    r2@@r3@@r4
class PatternFunc_e1r1e2_e1r2e3_and_e1r2e2_e1r2e3(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = dict()
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame, log_process=True):
        if len(self._pattern_dict) == 0:
            return
        use_gpu = False
        # if torch.cuda.is_available():
        #     try:
        #         import cudf
        #         print("using cudf ...")
        #         df = cudf.DataFrame.from_pandas(triples)
        #         use_gpu = True
        #     except :
        #         print("using pandas ...")
        #         print()
        #         df = triples
        # else:
        print("using pandas ...")
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern FunctionalProperty(r1), subPropertyOf(r1, r2)", disable=not log_process):
            r1 = g[0]
            if r1 in self._pattern_dict:
                r2_l = list(set(self._pattern_dict[r1]))
                r1_df = g[1]
                # (<e1 r2 e2> <e1 r2 e3> or <e1 r1 e2> <e1 r2 e3> ) and e2 != e3
                for r2 in r2_l:
                    if r2 not in gp.groups:
                        continue
                    r2_df = gp.get_group(r2)
                    # <e1 r2 e2> <e1 r2 e3>
                    df.update(r2_df[r2_df.duplicated('head', keep=False)].
                              query("is_new==True")['is_valid'].apply(lambda x: False))
                    # <e1 r1 e2> <e1 r2 e3> and e2 != e3
                    r1_head = r1_df['head']
                    r2_has_head_in_r2 = r2_df.query("head in @r1_head and is_new==True")
                    for idx, row in r1_df.iterrows():
                        x = row['head']
                        y = row['tail']
                        df.update(r2_has_head_in_r2.query("tail != @y and head == @x")['is_valid'].apply(lambda x: False))
        if use_gpu:
            print("back to cudf ...")
            df = df.head().to_pandas()
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
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
