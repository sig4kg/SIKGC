from __future__ import annotations
from pathlib import Path
import os

from abox_scanner.pattern12_scanner import Pattern12
from abox_scanner.pattern13_scanner import Pattern13
from abox_scanner.pattern1_scanner import Pattern1
from abox_scanner.pattern2_scanner import Pattern2
from abox_scanner.pattern5_scanner import Pattern5
from abox_scanner.pattern8_scanner import Pattern8
from abox_scanner.pattern9_scanner import Pattern9
from abox_scanner.pattern10_scanner import Pattern10
from abox_scanner.pattern11_scanner import Pattern11
from abox_scanner.pattern_pos_domain import PatternPosDomain
from abox_scanner.pattern_pos_range import PatternPosRange
from abox_scanner.abox_utils import ContextResources
import pandas as pd
import numpy as np
import datetime

# Author Sylvia Fangrong Wang

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
        self._IJP_strategies = []
        self._schema_correct_strategies = []
        self._id2strategy = {1: Pattern1,
                             2: Pattern2,
                             5: Pattern5,
                             8: Pattern8,
                             9: Pattern9,
                             10: Pattern10,
                             11: Pattern11,
                             12: Pattern12,
                             13: Pattern13,
                             'pos_domain': PatternPosDomain,
                             'pos_range': PatternPosRange}

    def set_triples_to_scan_int_df(self, hrt_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_df = hrt_int_df

        return self

    def register_patterns_all(self) -> AboxScannerScheduler:
        return self.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13], ['pos_domain', 'pos_range'])

    def register_pattern(self, neg_pattern_ids, pos_pattern_ids) -> AboxScannerScheduler:
        def regp(ids, stratege_l):
            for id in ids:
                pattern_file = f"TBoxPattern_{id}.txt"
                if pattern_file not in files:
                    print(f"the pattern file for patter id={id} does not exist in {self._tbox_pattern_dir}")
                    continue
                entry = os.path.join(self._tbox_pattern_dir, pattern_file)
                if id in self._id2strategy:
                    ps_class = self._id2strategy[id]
                    ps = ps_class(context_resources=self._context_resources)
                    ps.pattern_to_int(entry)
                    stratege_l.append(ps)

        files = os.listdir(self._tbox_pattern_dir)
        # for idx, file in enumerate(files):
        regp(neg_pattern_ids, self._IJP_strategies)
        regp(pos_pattern_ids, self._schema_correct_strategies)
        return self

    def scan_IJ_patterns(self, work_dir):
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        # aggregate triples by relation
        start_time = datetime.datetime.now()
        old_df = self._context_resources.hrt_int_df
        df = self._context_resources.hrt_to_scan_df[['head', 'rel', 'tail']]
        new_items = pd.concat([df, old_df, old_df]).drop_duplicates(keep=False)
        df['is_valid'] = True
        df['is_new'] = True
        if old_df is not None:
            mask = (df[['head', 'rel', 'tail']].isin(new_items[['head', 'rel', 'tail']])).all(axis=1)
            # pandas has defect with df[mask], it get same values as new_items.
            df.update(df[mask]['is_new'].apply(lambda x: False))

        init_invalid = len(df.query("is_valid == False"))
        for scanner in self._IJP_strategies:
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
        valids = valids.drop_duplicates(keep='first')
        if len(valids) > 0:
            valids = valids.astype(int)
        valids.to_csv(f"{work_dir}valid_hrt.txt", header=None, index=None, sep='\t', mode='a')
        print(f"total count: {len(self._context_resources.hrt_to_scan_df)}; invalids count: {str(len(invalids))}; valids count {str(len(valids))}")
        print(f"The scanning duration is {datetime.datetime.now() - start_time}")
        print(f"saving {work_dir}invalid_hrt.txt\nsaving {work_dir}valid_hrt.txt")
        return valids, invalids

    def scan_schema_correct_patterns(self, work_dir):
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        # aggregate triples by relation
        start_time = datetime.datetime.now()
        df = self._context_resources.hrt_to_scan_df[['head', 'rel', 'tail']]
        df['correct'] = True
        for scanner in self._schema_correct_strategies:
            print("Scanning schema pattern: " + str(type(scanner)))
            scanner.scan_pattern_df_rel(df)

        total_correct = len(df.query("correct == True"))
        print(f"identified schema correct triples count: {str(total_correct)}")
        out_path = Path(work_dir)
        if not out_path.parent.exists():
            out_path.parent.mkdir(exist_ok=False)
        correct = df.query("correct == True")[['head', 'rel', 'tail']]
        correct = correct.drop_duplicates(keep="first")
        if len(correct) > 0:
            correct = correct.astype(int)
        correct.to_csv(f"{work_dir}schema_correct_hrt.txt", header=None, index=None, sep='\t', mode='a')
        print(f"scanned total count: {len(self._context_resources.hrt_to_scan_df)}; schema correct count: {str(len(correct))}")
        print(f"The scanning duration is {datetime.datetime.now() - start_time}")
        print(f"saving {work_dir}schema_correct_hrt.txt")
        return correct



