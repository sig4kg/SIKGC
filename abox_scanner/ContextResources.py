from abc import ABC, abstractmethod
from functools import reduce
import os.path as osp
import pandas as pd
from abox_scanner.abox_utils import *

class PatternScanner(ABC):
    @abstractmethod
    def pattern_to_int(self, file_entry):
        pass

    @abstractmethod
    def scan_pattern_df_rel(self, triples: pd.DataFrame, log_process=True):
        pass


class ContextResources:
    def __init__(self, original_hrt_triple_file_path, class_and_op_file_path, work_dir):
        if len(work_dir) > 0:
            init_dir(work_dir)
        self.class2id = class2id(class_and_op_file_path + 'AllClasses.txt')
        self.op2id = op2id(class_and_op_file_path + 'AllObjectProperties.txt')
        # h, r, t
        all_triples = read_original_hrt_triples_to_list(original_hrt_triple_file_path)
        self.original_hrt_count = len(all_triples)
        self.ent2id, self.hrt_to_scan_df = hrt_original2int(all_triples, self.op2id, self.class2id)
        self.hrt_int_df = None
        self.hrt_to_scan_type_df = None
        self.classid2class = {self.class2id[key]: key for key in self.class2id}
        self.entid2classids = entid2classid(self.ent2id, self.class2id, class_and_op_file_path + "entity2type.txt")
        self.id2ent = {self.ent2id[key]: key for key in self.ent2id}
        self.id2op = {self.op2id[key]: key for key in self.op2id}
        self.silver_rel = None
        self.silver_type = None
        self.work_dir = work_dir
        self.entid2text = dict()
        self.relid2text = dict()

    def load_id2literal(self):
        file_path = osp.join(self.work_dir, 'entity2text.txt')
        if not osp.exists(file_path):
            return
        with open(file_path) as f:
            for line in f:
                values = line.strip().split('\t')
                entity = values[0]
                text = values[1]
                if entity not in self.ent2id:
                    continue
                ent_id = self.ent2id[entity]
                self.entid2text.update({ent_id: text})
        file_path = osp.join(self.work_dir, 'relation2text.txt')
        if not osp.exists(file_path):
            return
        with open(file_path) as f:
            for line in f:
                values = line.strip().split('\t')
                rel = values[0]
                text = values[1]
                if rel not in self.op2id:
                    continue
                rel_id = self.op2id[rel]
                self.relid2text.update({rel_id: text})

    def get_type_count(self):
        self.type_count = reduce(lambda x,y: x + y, [len(v) for v in self.entid2classids.values()])
        return self.type_count

    def type2hrt_int_df(self) -> pd.DataFrame:
        type_hrt = []
        for entid in self.entid2classids:
            h = entid
            r = 0
            typeOfe = self.entid2classids[entid]
            ent_type_hrt = [[h, r, t] for t in typeOfe]
            type_hrt.extend(ent_type_hrt)
        type_df = pd.DataFrame(data=type_hrt, columns=['head', 'rel', 'tail'])
        return type_df

    def df2nt(self, hrt_df, work_dir):
        rdf_nt = []
        for idx, row in hrt_df.iterrows():
            h = self.id2ent[row['head']]
            r = self.id2op[row['rel']]
            t = self.id2ent[row['tail']]
            rdf_nt.append(['<' + h + '>', '<' + r + '>', '<' + t + '>'])
        with open(work_dir + "abox.nt", 'w') as f:
            print(f"Saving to {work_dir}abox.nt")
            for line in rdf_nt:
                f.write(f'''{line[0]} {line[1]} {line[2]} .\n''')

    def type2nt(self, work_dir):
        # get entity types
        rdf_type = []
        r = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        individual = "<http://www.w3.org/2002/07/owl#NamedIndividual>"
        for entid in self.entid2classids:
            h = self.id2ent[entid]
            rdf_type.append(['<' + h + '>', r, individual])
            typeOfs = self.entid2classids[entid]
            for t in typeOfs:
                if t in self.classid2class:
                    rdf_type.append(['<' + h + '>', r, f'''<{self.classid2class[t]}>'''])
        with open(work_dir + "type.nt", 'w') as f:
            print(f"Saving to {work_dir}type.nt")
            for line in rdf_type:
                f.write(f'''{line[0]} {line[1]} {line[2]} .\n''')
        return rdf_type

    def to_ntriples(self, work_dir, schema_in_nt=''):
        self.df2nt(self.hrt_int_df, work_dir)
        self.type2nt(work_dir)
        wait_until_file_is_saved(work_dir + "abox.nt", 180)
        wait_until_file_is_saved(work_dir + "type.nt", 180)
        if schema_in_nt != "":
            os.system(f"cat {schema_in_nt} {work_dir}abox.nt {work_dir}type.nt> {work_dir}tbox_abox.nt")

    # def type_ntriples(self, work_dir, schema_in_nt=''):
    #     df_types = self.type2nt()
    #     # create individual declaration
    #     print(f"Saving to {work_dir}type.nt")
    #     df_types.to_csv(work_dir + "type.nt",  header=False, index=False, sep=' ')
    #     wait_until_file_is_saved(work_dir + "type.nt", 180)
    #     if schema_in_nt != "":
    #         os.system(f"cat {schema_in_nt} {work_dir}type.nt > {work_dir}tbox_type.ttl")
