#range
from abox_scanner.abox_utils import PatternScanner


class Pattern2(PatternScanner):
    def __init__(self, class2int, node2class_int) -> None:
        self._class2int = class2int
        self._node2class_int = node2class_int
        self._pattern_dict = None

    def scan_pattern_df_rel(self, aggregated_triples):
        df = aggregated_triples
        rel = df.iloc[0]['rel']
        if rel not in self._pattern_dict:
            return
        else:
            invalid = self._pattern_dict[rel]['invalid']
            for idx, row in df.iterrows():
                if self._node2class_int[row['tail']] in invalid:
                    df.loc[idx, 'is_valid'] = False
        return df

    #   input the path of TBox scanner output, including a class list and 7 rule patterns
    #   return class2int dict and rule2int dict
    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                ont1 = self._class2int[items[0][1:][:-1].split('/')[-1]]
                ont2 = self._class2int[items[1][1:][:-1].split('/')[-1]]
                disjoint = [self._class2int[ii[1:][:-1].split('/')[-1]] for ii in items[2][:-2].split('\"') if ii not in ['owl:Nothing']]
                pattern_dict.update({ont1: {'valid': ont2, 'invalid': disjoint}})
            self._pattern_dict = pattern_dict
