from __future__ import annotations
from typing import List
import os
import pandas as pd
from abox_scanner.pattern1_scanner import Pattern1
from abox_scanner.pattern2_scanner import Pattern2
from abox_scanner.abox_utils import PatternScanner


class AboxScannerScheduler:
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(self, tbox_pattern_input_dir, class2int, node2class_int, all_triples_int):
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._input_dir = tbox_pattern_input_dir
        self._class2int = class2int
        self._node2class_int = node2class_int
        self._all_triples_int = all_triples_int
        self._strategies = []
        self._id2patternfile = {1: "TBoxPattern_1.txt", 2: "TBoxPattern_2.txt"}
        self._id2strategy = {1: Pattern1, 2: Pattern2}

    def register_pattern(self, pattern_ids) -> None:
        files = os.listdir(self._input_dir)
        # for idx, file in enumerate(files):
        for id in pattern_ids:
            if self._id2patternfile[id] not in files:
                print(f"the pattern file for patter id={id} does not exist in {self._input_dir}")
                continue
            entry = os.path.join(self._input_dir, self._id2patternfile[id])
            ps_class = self._id2strategy[id]
            ps = ps_class(self._class2int, self._node2class_int)
            ps.pattern_to_int(entry)
            self._strategies.append(ps)


    def scan_patterns(self, output_dir) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        # aggregate triples by relation
        df = pd.DataFrame(self._all_triples_int, columns=['head', 'rel', 'tail'])
        df['is_valid'] = True
        for scanner in self._strategies:
            df = df.query("is_valid == True").groupby('rel').apply(lambda x: scanner.scan_pattern_df_rel(x))

        df.query("is_valid == False")[['head', 'rel', 'tail']].to_csv(f"{output_dir}/invalid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        df.query("is_valid == True")[['head', 'rel', 'tail']].to_csv(f"{output_dir}/valid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        print("done")



