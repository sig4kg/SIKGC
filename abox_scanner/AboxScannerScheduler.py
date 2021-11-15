from __future__ import annotations
from pathlib import Path
import os
from abox_scanner.pattern1_scanner import Pattern1
from abox_scanner.pattern2_scanner import Pattern2
from abox_scanner.pattern5_scanner import Pattern5
from abox_scanner.pattern8_scanner import Pattern8
from abox_scanner.pattern9_scanner import Pattern9
from abox_scanner.pattern10_scanner import Pattern10
from abox_scanner.pattern11_scanner import Pattern11
from abox_scanner.abox_utils import ContextResources
import numpy as np

class AboxScannerScheduler:
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(self, tbox_pattern_dir, context_resources: ContextResources):
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._tbox_pattern_dir = tbox_pattern_dir
        self._context_resources = context_resources
        self._strategies = []
        self._id2strategy = {1: Pattern1, 2: Pattern2, 5: Pattern5, 8: Pattern8, 9: Pattern9, 10: Pattern10, 11: Pattern11}

    def set_triples_to_scan_int_df(self, hrt_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_df = hrt_int_df
        return self

    def register_pattern(self, pattern_ids) -> AboxScannerScheduler:
        files = os.listdir(self._tbox_pattern_dir)
        # for idx, file in enumerate(files):
        for id in pattern_ids:
            pattern_file = f"TBoxPattern_{id}.txt"
            if pattern_file not in files:
                print(f"the pattern file for patter id={id} does not exist in {self._tbox_pattern_dir}")
                continue
            entry = os.path.join(self._tbox_pattern_dir, pattern_file)
            if id in self._id2strategy:
                ps_class = self._id2strategy[id]
                ps = ps_class(context_resources=self._context_resources)
                ps.pattern_to_int(entry)
                self._strategies.append(ps)
        return self

    def scan_patterns(self, work_dir) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        # aggregate triples by relation
        df = self._context_resources.hrt_to_scan_df[['head', 'rel', 'tail']]
        df['is_valid'] = True
        init_invalid = len(df.query("is_valid == False"))
        for scanner in self._strategies:
            print("Scanning schema pattern: " + str(type(scanner)))
            scanner.scan_pattern_df_rel(df)
            total_invalid = len(df.query("is_valid == False"))
            print(f"identified invalid triples count: {str(total_invalid - init_invalid)}")
            init_invalid = total_invalid
        out_path = Path(work_dir)
        if not out_path.parent.exists():
            out_path.parent.mkdir(exist_ok=False)
        invalids = df.query("is_valid == False")[['head', 'rel', 'tail']]
        if len(invalids) > 0:
            invalids = invalids.astype(int)
        invalids.to_csv(f"{work_dir}invalid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        valids = df.query("is_valid == True")[['head', 'rel', 'tail']]
        if len(valids) > 0:
            valids = valids.astype(int)
        valids.to_csv(f"{work_dir}valid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        print(f"total count: {len(self._context_resources.hrt_to_scan_df)}; invalids count: {str(len(invalids))}; valids count {str(len(valids))}")
        print(f"saving {work_dir}invalid_hrt.txt\nsaving {work_dir}valid_hrt.txt")




