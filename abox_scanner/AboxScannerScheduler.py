from __future__ import annotations
from pathlib import Path
import os
from abox_scanner.pattern12_scanner import Pattern12
from abox_scanner.pattern13_scanner import Pattern13
from abox_scanner.pattern15_scanner import Pattern15
from abox_scanner.pattern1_scanner import Pattern1
from abox_scanner.pattern2_scanner import Pattern2
from abox_scanner.pattern5_scanner import Pattern5
from abox_scanner.pattern8_scanner import Pattern8
from abox_scanner.pattern9_scanner import Pattern9
from abox_scanner.pattern10_scanner import Pattern10
from abox_scanner.pattern11_scanner import Pattern11
from abox_scanner.pattern_pos_domain import PatternPosDomain
from abox_scanner.pattern_pos_range import PatternPosRange
from abox_scanner.pattern_gen_inverse import *
from abox_scanner.pattern_gen_subproperty import *
# from abox_scanner.pattern_gen_reflexive import *
from abox_scanner.pattern_gen_symetric import *
from abox_scanner.pattern_gen_transitive import *
from abox_scanner.ContextResources import ContextResources, wait_until_file_is_saved
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
        self._schema_gen_strategies = []
        self._id2strategy = {1: Pattern1,
                             2: Pattern2,
                             5: Pattern5,
                             8: Pattern8,
                             9: Pattern9,
                             10: Pattern10,
                             11: Pattern11,
                             12: Pattern12,
                             13: Pattern13,
                             15: Pattern15,
                             'pos_domain': PatternPosDomain,
                             'pos_range': PatternPosRange,
                             'inverse': PatternGenInverse,
                             'symetric': PatternGenSymetric,
                             'subproperty': PatternGenSubproperty,
                             # 'reflexive': PatternGenReflexive,
                             'transitive': PatternGenTransitive
                             }

    def set_triples_to_scan_int_df(self, hrt_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_df = hrt_int_df
        return self

    def register_patterns_all(self) -> AboxScannerScheduler:
        return self.register_pattern([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15], ['pos_domain', 'pos_range'])

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

    def register_gen_pattern(self) -> AboxScannerScheduler:
        files = os.listdir(self._tbox_pattern_dir)
        for id in ['inverse', 'symetric', 'subproperty', 'transitive']:
            pattern_file = f"TBoxPattern_gen_{id}.txt"
            if pattern_file not in files:
                print(f"the pattern gen file for patter id={id} does not exist in {self._tbox_pattern_dir}")
                continue
            entry = os.path.join(self._tbox_pattern_dir, pattern_file)
            if id in self._id2strategy:
                ps_class = self._id2strategy[id]
                ps = ps_class(context_resources=self._context_resources)
                ps.pattern_to_int(entry)
                self._schema_gen_strategies.append(ps)
        return self

    def scan_IJ_patterns(self, work_dir, save_result=True):
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        # aggregate triples by relation
        start_time = datetime.datetime.now()
        old_df = self._context_resources.hrt_int_df
        df = self._context_resources.hrt_to_scan_df
        df['is_valid'] = True
        if old_df is not None:
            df['is_new'] = False
            # mask = (df[['head', 'rel', 'tail']].isin(old_df[['head', 'rel', 'tail']])).all(axis=1)
            # pandas has defect with df[mask], it get same values as new_items.
            # df.update(df[mask]['is_new'].apply(lambda x: False))
            to_filter_out = old_df[['head', 'rel', 'tail']]
            ind = pd.concat([df[['head', 'rel', 'tail']], to_filter_out, to_filter_out]).drop_duplicates(keep=False).index
            new_column = pd.Series([True for i in ind], name='is_new', index=ind)
            df.update(new_column)
            del to_filter_out
            del new_column
        else:
            df['is_new'] = True

        init_invalid = len(df.query("is_valid == False"))
        for scanner in self._IJP_strategies:
            # print("Scanning schema pattern: " + str(type(scanner)))
            scanner.scan_pattern_df_rel(df)
            total_invalid = len(df.query("is_valid == False"))
            print(f"{str(type(scanner))} identified invalid triples count: {str(total_invalid - init_invalid)}")
            init_invalid = total_invalid
        # split result
        invalids = df.query("is_valid == False")[['head', 'rel', 'tail']]
        if len(invalids) > 0:
            invalids = invalids.astype(int)
        valids = df.query("is_valid == True")[['head', 'rel', 'tail']]
        if len(valids) > 0:
            valids = valids.astype(int)
        print(f"total count: {len(self._context_resources.hrt_to_scan_df)}; invalids count: {str(len(invalids.index))}; valids count {str(len(valids.index))}")
        print(f"consistency ratio: {str(len(valids.index) / len(df.index))}")
        print(f"The scanning duration is {datetime.datetime.now() - start_time}")
        # save invalids for negative sampling, we convert hrt_int to original uri,
        # because the blp text files use the original uri as keys.
        if save_result:
            out_path = Path(work_dir)
            if not out_path.parent.exists():
                out_path.parent.mkdir(exist_ok=False)
            invalid_uris = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
            invalid_uris[['head', 'tail']] = invalids[['head', 'tail']].applymap(
                lambda x: self._context_resources.id2ent[x])  # to int
            invalid_uris['rel'] = invalids['rel'].apply(
                lambda x: self._context_resources.id2op[x])  # to int
            invalid_uris.to_csv(f"{work_dir}invalid_hrt.txt", header=False, index=False, sep='\t', mode='a')
            valids.to_csv(f"{work_dir}valid_hrt.txt", header=None, index=None, sep='\t', mode='w')
            print(f"saving {work_dir}invalid_hrt.txt\nsaving {work_dir}valid_hrt.txt")
            wait_until_file_is_saved(f"{work_dir}invalid_hrt.txt")
        return valids, invalids

    def scan_schema_correct_patterns(self, work_dir):
        start_time = datetime.datetime.now()
        df = self._context_resources.hrt_to_scan_df
        df['correct'] = True
        init_correct = len(df.query("correct == False"))
        for scanner in self._schema_correct_strategies:
            print("Scanning schema pattern: " + str(type(scanner)))
            scanner.scan_pattern_df_rel(df)
            total_correct = len(df.query("is_valid == False"))
            print(f"{str(type(scanner))} identified incorrect triples count: {str(total_correct - init_correct)}")
            init_correct = total_correct
        total_correct = len(df.query("correct==True"))
        print(f"identified schema correct triples count: {str(total_correct)}")
        print(f"correctness ratio: {str(total_correct / len(df.index))}")
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
        inco_valid = df.query("correct == False and is_valid==True")[['head', 'rel', 'tail']]
        inco_valid[['head', 'tail']] = inco_valid[['head', 'tail']].applymap(lambda x: self._context_resources.id2ent[x])  # to int
        inco_valid[['rel']] = inco_valid[['rel']].applymap(lambda x: self._context_resources.id2op[x])
        inco_valid.to_csv(f"{work_dir}incorrect_valid_uri.txt", header=None, index=None, sep='\t', mode='a')
        return correct

    # the generator patterns are used to generate new triples base on schema
    def scan_generator_patterns(self) -> pd.DataFrame:
        if len(self._schema_gen_strategies) == 0:
            self.register_gen_pattern()
        start_time = datetime.datetime.now()
        df = self._context_resources.hrt_int_df
        new_df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        for scanner in self._schema_gen_strategies:
            print("Scanning generator pattern: " + str(type(scanner)))
            tmp_df = scanner.scan_pattern_df_rel(df)
            count_new = len(tmp_df.index)
            if count_new == 0:
                continue
            new_df = pd.concat([new_df, tmp_df]).drop_duplicates(keep='first').reset_index(drop=True)
            print(f"{str(type(scanner))} inferred new triples count: {str(count_new)}")
        print(f"The abox gen reasoning duration is {datetime.datetime.now() - start_time}")
        return new_df



