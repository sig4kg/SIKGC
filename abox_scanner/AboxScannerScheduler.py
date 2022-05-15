from __future__ import annotations
from pathlib import Path
import os

from abox_scanner.PatternAsymmetric import PatternAsymmetric
from abox_scanner.PatternFunc_e1r1e2_e1r1e3 import PatternFunc_e1r1e2_e1r1e3
from abox_scanner.PatternFunc_e1r1e2_e1r2e3_and_e1r2e2_e1r2e3 import PatternFunc_e1r1e2_e1r2e3_and_e1r2e2_e1r2e3
from abox_scanner.PatternFunc_e1r1e2_e3r2e1_and_e2r2e1_e3r2e1 import PatternFunc_e1r1e2_e3r2e1_and_e2r2e1_e3r2e1
from abox_scanner.PatternIrreflexive import PatternIrreflexive
from abox_scanner.PatternNegDomain import PatternNegDomain
from abox_scanner.PatternNegRange import PatternNegRange
from abox_scanner.PatternPosDomain import PatternPosDomain
from abox_scanner.PatternPosRange import PatternPosRange
from abox_scanner.ContextResources import ContextResources, wait_until_file_is_saved
import pandas as pd
import datetime
from abox_scanner.PatternTypeDisjointC import PatternTypeDisjointC
from abox_scanner.PatternTypeDisjointER import PatternTypeDisjointER
from abox_scanner.PatternTypeDisjointERInvs import PatternTypeDisjointERInvs
from abox_scanner.Pattern_e1r1e2_e1r2e3 import Pattern_e1r1e2_e1r2e3
from abox_scanner.Pattern_e1r1e2_e3r2e1 import Pattern_e1r1e2_e3r2e1
from abox_scanner.Pattern_e2r1e1_e1r2e3 import Pattern_e2r1e1_e1r2e3
from abox_scanner.Pattern_e2r1e1_e3r2e1 import Pattern_e2r1e1_e3r2e1


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
        self._rel_IJP_strategies = []
        self._schema_correct_strategies = []
        self._type_IJP_strategies = []
        self._id2strategy = {1: PatternNegDomain,
                             2: PatternNegRange,
                             3: Pattern_e1r1e2_e1r2e3,
                             4: Pattern_e1r1e2_e3r2e1,
                             5: Pattern_e2r1e1_e1r2e3,
                             6: Pattern_e2r1e1_e3r2e1,
                             7: PatternFunc_e1r1e2_e1r1e3,
                             8: PatternFunc_e1r1e2_e1r2e3_and_e1r2e2_e1r2e3,
                             9: PatternFunc_e1r1e2_e3r2e1_and_e2r2e1_e3r2e1,
                             10: PatternIrreflexive,
                             11: PatternAsymmetric,
                             12: PatternTypeDisjointC,
                             13: PatternTypeDisjointER,
                             14: PatternTypeDisjointERInvs,
                             15: PatternPosDomain,
                             16: PatternPosRange
                             }

    def set_triples_to_scan_int_df(self, hrt_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_df = hrt_int_df
        return self

    def set_triples_to_scan_type_df(self, type_int_df) -> AboxScannerScheduler:
        self._context_resources.hrt_to_scan_type_df = type_int_df
        return self

    def register_patterns_all(self) -> AboxScannerScheduler:
        self.register_patterns([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], self._rel_IJP_strategies)
        self.register_patterns([12, 13, 14], self._type_IJP_strategies)
        self.register_patterns([15, 16], self._schema_correct_strategies)
        return self

    def register_patterns(self, ids: [], stratege_l: []):
        files = os.listdir(self._tbox_pattern_dir)
        for id in ids:
            name = self._id2strategy[id].__name__
            pattern_file = f"{name}.txt"
            if pattern_file not in files:
                print(f"the pattern file for patter id={id} does not exist in {self._tbox_pattern_dir}")
                continue
            entry = os.path.join(self._tbox_pattern_dir, pattern_file)
            if id in self._id2strategy:
                ps_class = self._id2strategy[id]
                ps = ps_class(context_resources=self._context_resources)
                ps.pattern_to_int(entry)
                stratege_l.append(ps)

    def scan_rel_IJPs(self, work_dir, save_result=True):
        # aggregate triples by relation
        start_time = datetime.datetime.now()
        old_df = self._context_resources.hrt_int_df
        # df = self._context_resources.hrt_to_scan_df.query("rel != 0")   # rel == 0 is rdf:type
        df = self._context_resources.hrt_to_scan_df
        df['is_valid'] = True
        if old_df is not None:
            df['is_new'] = False
            # mask = (df[['head', 'rel', 'tail']].isin(old_df[['head', 'rel', 'tail']])).all(axis=1)
            # pandas has defect with df[mask], it get same values as new_items.
            # df.update(df[mask]['is_new'].apply(lambda x: False))
            to_filter_out = old_df[['head', 'rel', 'tail']]
            ind = pd.concat([df[['head', 'rel', 'tail']], to_filter_out, to_filter_out]).drop_duplicates(
                keep=False).index
            new_column = pd.Series([True for i in ind], name='is_new', index=ind)
            df.update(new_column)
            del to_filter_out
            del new_column
        else:
            df['is_new'] = True

        init_invalid = len(df.query("is_valid == False"))
        for scanner in self._rel_IJP_strategies:
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
        print(
            f"total count: {len(self._context_resources.hrt_to_scan_df)}; invalids count: {str(len(invalids.index))}; valids count {str(len(valids.index))}")
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
        print(
            f"scanned total count: {len(self._context_resources.hrt_to_scan_df)}; schema correct count: {str(len(correct))}")
        print(f"The scanning duration is {datetime.datetime.now() - start_time}")
        print(f"saving {work_dir}schema_correct_hrt.txt")
        inco_valid = df.query("correct == False and is_valid==True")[['head', 'rel', 'tail']]
        inco_valid[['head', 'tail']] = inco_valid[['head', 'tail']].applymap(
            lambda x: self._context_resources.id2ent[x])  # to int
        inco_valid[['rel']] = inco_valid[['rel']].applymap(lambda x: self._context_resources.id2op[x])
        inco_valid.to_csv(f"{work_dir}incorrect_valid_uri.txt", header=None, index=None, sep='\t', mode='a')
        return correct

    def scan_type_IJPs(self, work_dir, save_result=True):
        # aggregate triples by relation
        start_time = datetime.datetime.now()
        df = self._context_resources.hrt_to_scan_type_df
        old_type_hrt_df = self._context_resources.type2hrt_int_df()
        df['is_valid'] = True
        df['is_new'] = False
        to_filter_out = old_type_hrt_df
        ind = pd.concat([df[['head', 'rel', 'tail']], to_filter_out, to_filter_out]).drop_duplicates(
            keep=False).index
        new_column = pd.Series([True for i in ind], name='is_new', index=ind)
        df.update(new_column)
        del new_column
        init_invalid = len(df.query("is_valid == False"))
        for scanner in self._type_IJP_strategies:
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
        print(
            f"total count: {len(df.index)}; invalids count: {str(len(invalids.index))}; valids count {str(len(valids.index))}")
        print(f"consistency ratio: {str(len(valids.index) / len(df.index))}")
        print(f"The scanning duration is {datetime.datetime.now() - start_time}")
        # save invalids for negative sampling, we convert hrt_int to original uri,
        # because the blp text files use the original uri as keys.
        if save_result:
            out_path = Path(work_dir)
            if not out_path.parent.exists():
                out_path.parent.mkdir(exist_ok=False)
            invalid_uris = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
            invalid_uris[['head']] = invalids[['head']].applymap(
                lambda x: self._context_resources.id2ent[x])  # to int
            invalid_uris[['tail']] = invalids[['tail']].applymap(
                lambda x: self._context_resources.classid2class[x])  # to int
            invalid_uris['rel'] = invalids['rel'].apply(
                lambda x: self._context_resources.id2op[x])  # to int
            invalid_uris.to_csv(f"{work_dir}invalid_type_hrt.txt", header=False, index=False, sep='\t', mode='a')
            valids.to_csv(f"{work_dir}valid_type_hrt.txt", header=None, index=None, sep='\t', mode='w')
            print(f"saving {work_dir}invalid_type_hrt.txt\nsaving {work_dir}valid_type_hrt.txt")
            wait_until_file_is_saved(f"{work_dir}invalid_type_hrt.txt")
        return valids, invalids