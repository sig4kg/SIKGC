from __future__ import annotations
from pathlib import Path
import os
from abox_scanner.pattern1_scanner import Pattern1
from abox_scanner.pattern2_scanner import Pattern2
from abox_scanner.abox_utils import ContextResources


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
        self._id2patternfile = {1: "TBoxPattern_1.txt", 2: "TBoxPattern_2.txt"}
        self._id2strategy = {1: Pattern1, 2: Pattern2}

    def set_triples_int_df(self, hrt_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_df = hrt_int_df
        return self


    def register_pattern(self, pattern_ids) -> AboxScannerScheduler:
        files = os.listdir(self._tbox_pattern_dir)
        # for idx, file in enumerate(files):
        for id in pattern_ids:
            if self._id2patternfile[id] not in files:
                print(f"the pattern file for patter id={id} does not exist in {self._tbox_pattern_dir}")
                continue
            entry = os.path.join(self._tbox_pattern_dir, self._id2patternfile[id])
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
        for scanner in self._strategies:
            df = df.query("is_valid == True").groupby('rel').apply(lambda x: scanner.scan_pattern_df_rel(x))
        out_path = Path(work_dir)
        if not out_path.parent.exists():
            out_path.parent.mkdir(exist_ok=False)
        df.query("is_valid == False")[['head', 'rel', 'tail']].to_csv(f"{work_dir}invalid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        df.query("is_valid == True")[['head', 'rel', 'tail']].to_csv(f"{work_dir}valid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        print(f"saving {work_dir}invalid_hrt.txt\nsaving {work_dir}valid_hrt.txt")




