from abc import ABC, abstractmethod
from functools import reduce

import pandas as pd
from abox_scanner.abox_utils import *

class PatternScanner(ABC):
    @abstractmethod
    def pattern_to_int(self, file_entry):
        pass

    @abstractmethod
    def scan_pattern_df_rel(self, triples: pd.DataFrame):
        pass


class ContextResources:
    def __init__(self, original_hrt_triple_file_path, class_and_op_file_path, work_dir, create_id_file=False):
        init_workdir(work_dir)
        # h, r, t
        all_triples = read_original_hrt_triples_to_list(original_hrt_triple_file_path)
        self.original_train_count = len(all_triples)
        self.ent2id, self.rel2id, self.hrt_to_scan_df = hrt_original2int(all_triples,
                                                                         f"{work_dir}train/",
                                                                         create_id_file=create_id_file)
        self.hrt_int_df = None
        self.class2id = class2id(class_and_op_file_path + 'AllClasses.txt')
        self.classid2class = {self.class2id[key]: key for key in self.class2id}
        self.op2id = op2id(class_and_op_file_path + 'AllObjectProperties.txt', self.rel2id)
        self.entid2classids = entid2classid(self.ent2id, self.class2id, class_and_op_file_path + "entity2type.txt")
        self.id2ent = {self.ent2id[key]: key for key in self.ent2id}
        self.id2op = {self.op2id[key]: key for key in self.op2id}
        self.type_count = reduce(lambda x,y: x + y, [len(v) for v in self.entid2classids.values()])

    def type2nt(self) -> pd.DataFrame:
        # get entity types
        rdf_type = []
        r = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        individual  = "<http://www.w3.org/2002/07/owl#NamedIndividual>"
        for entid in self.entid2classids:
            h = self.id2ent[entid]
            rdf_type.append([f"<{h}>", r, individual])
            typeOfs = self.entid2classids[entid]
            for t in typeOfs:
                if t in self.classid2class:
                    rdf_type.append([f"<{h}>", r, f"<{self.classid2class[t]}>"])
        df_types = pd.DataFrame(data=rdf_type, columns=['head', 'rel', 'tail'])
        df_types['dot'] = '.'
        return df_types

    def to_ntriples(self, work_dir, schema_in_nt=''):
        df = self.hrt_int_df.copy(deep=True)
        df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: '<' + self.id2ent[x] + '>')
        df[['rel']] = df[['rel']].applymap(lambda x: '<' + self.id2op[x] + '>')  # to int
        df['dot'] = '.'
        df_types = self.type2nt()
        # create individual declaration
        expanded_df = pd.concat([df_types, df])
        print(f"Saving to {work_dir}abox.nt")
        expanded_df.to_csv(work_dir + "abox.nt",  header=False, index=False, sep=' ')
        wait_until_file_is_saved(work_dir + "abox.nt", 180)
        if schema_in_nt != "":
            os.system(f"cat {schema_in_nt} {work_dir}abox.nt > {work_dir}tbox_abox.nt")

    def type_ntriples(self, work_dir, schema_in_nt=''):
        df_types = self.type2nt()
        # create individual declaration
        print(f"Saving to {work_dir}type.nt")
        df_types.to_csv(work_dir + "type.nt",  header=False, index=False, sep=' ')
        wait_until_file_is_saved(work_dir + "type.nt", 180)
        if schema_in_nt != "":
            os.system(f"cat {schema_in_nt} {work_dir}type.nt > {work_dir}tbox_type.ttl")

