from abox_scanner.ContextResources import PatternScanner, ContextResources
import pandas as pd
from tqdm import tqdm


# FunctionalProperty(r) ----- <x r y> <x r z>
class PatternFunc_e1r1e2_e1r1e3(PatternScanner):
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_set = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, triples: pd.DataFrame, log_process=True):
        if len(self._pattern_set) == 0:
            return
        df = triples
        gp = df.query("is_valid == True").groupby('rel', group_keys=True, as_index=False)
        for g in tqdm(gp, desc="scanning pattern Func_e1r1e2_e1r1e3", disable=not log_process):
            r = g[0]
            if r in self._pattern_set:
                r_triples_df = g[1]
                # if neg_sampling:
                    # duplicate heads and different is_new
                df.update(r_triples_df[r_triples_df.duplicated('head', keep=False)].
                                    query("is_new==True")['is_valid'].apply(lambda x: False))
        return df

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_set = set()
            lines = f.readlines()
            for l in lines:
                r = l.strip()[1:-1]
                if r in self._context_resources.op2id:
                    op = self._context_resources.op2id[r]
                    pattern_set.add(op)
            self._pattern_set = pattern_set
