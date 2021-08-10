from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import os
import time


ONTOLOGY_PATH = "../resources/NELL.ontology.ttl"
TBOX_PATTERNS_PATH = "../resources/NELL_patterns"
ALL_CLASS_FILE = "../resources/NELL-995/AllClasses.txt"
ALL_OP_FILE = "../resources/NELL-995/AllObjectProperties.txt"
ORIGINAL_TRIPLES_PATH = "../resources/NELL-995/NELLKG0.txt"


# NELL h, r, t
def read_original_hrt_triples_to_list(in_path):
    hrt_triples = []
    with open(in_path) as f:
        lines = f.readlines()
        for l in lines:
            items = l.split('\t')
            head = items[0].strip()
            tail = items[2].strip()
            rel = items[1].strip()
            if len(head) > 0 and len(tail) > 0 and len(rel) > 0:
                hrt_triples.append([head, rel, tail])
    # hrt_triples.sort(key=lambda x: x[1])
    return hrt_triples


def read_hrt_2_df(hrt_triples_file):
    df = pd.read_csv(
        hrt_triples_file, header=None, names=['head', 'rel', 'tail'], sep="\t")
    return df


def read_scanned_2_context_df(work_dir, context_resources: ContextResources):
    df = read_hrt_2_df(work_dir + "valid_hrt.txt")
    context_resources.hrt_int_df = df


def hrt_original2int(hrt_triples, out_dir, create_id_file=False):
    ent2id = dict()
    rel2id = dict()
    e_id = 0
    r_id = 0
    hrt_int = []
    for tri in hrt_triples:
        if tri[0] not in ent2id:
            ent2id.update({tri[0]: e_id})
            e_id += 1
        if tri[2] not in ent2id:
            ent2id.update({tri[2]: e_id})
            e_id += 1
        if tri[1] not in rel2id:
            rel2id.update({tri[1]: r_id})
            r_id +=1
        hrt_int.append([ent2id[tri[0]], rel2id[tri[1]], ent2id[tri[2]]])
    hrt_int_df = pd.DataFrame(data=hrt_int, columns=['head', 'rel', 'tail'])
    if create_id_file:
        # htr_new_lines = ''.join([f"{tri[0]} {tri[2]} {tri[1]}\n" for tri in hrt_int])
        # htr_new_lines = f"{len(hrt_int)}\n" + htr_new_lines
        # save_file(htr_new_lines, out_dir + "/train2id.txt")
        ent2id_lines = ''.join([f"{ent}\t{id}\n" for ent, id in ent2id.items()])
        ent2id_lines = f"{len(ent2id)}\n" + ent2id_lines
        save_file(ent2id_lines, out_dir + "/entity2id.txt")
        rel2id_lines = ''.join([f"{rel}\t{id}\n" for rel, id in rel2id.items()])
        rel2id_lines = f"{len(rel2id)}\n" + rel2id_lines
        save_file(rel2id_lines, out_dir + "/relation2id.txt")
    return ent2id, rel2id, hrt_int_df


def class2id(class_input):
    class2id = dict()
    with open(class_input) as f:
        lines = f.readlines()
        id_count = 0
        for l in lines:
            class_short = l.strip()
            if class_short not in class2id:
                class2id.update({class_short: id_count})
                id_count += 1
    return class2id


def op2id(op_file, rel2id):
    op2id = dict()
    with open(op_file) as f:
        lines = f.readlines()
        idx = len(rel2id)
        for l in lines:
            ls = l.strip()
            if ls in rel2id:
                op2id.update({ls: rel2id[ls]})
            else:
                op2id.update({ls: idx})
                idx += 1
    return op2id


def save_file(text, out_filename):
    out_path = Path(out_filename)
    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=False)
    with open(out_path, encoding='utf-8', mode='w') as out_f:
        out_f.write(text)
    out_f.close()   # wait until file is saved


def wait_until_file_is_saved(file_path: str, timeout_sec=10) -> bool:
    time_counter = 0
    interval = int(timeout_sec / 10) if timeout_sec > 10 else 1
    # print(f"waiting for saving {file_path} ...")
    while not os.path.exists(file_path):
        time.sleep(interval)
        time_counter += interval
        # print(f"waiting {time_counter} sec.")
        if time_counter > timeout_sec:
            # print(f"saving {file_path} timeout")
            break
    return os.path.exists(file_path)



def entid2classid_nell(ent2id, class2id):
    entid2classid = dict()
    for ent in ent2id:
        concept = ent.split('_', 1)[0]
        if concept in class2id:
            entid2classid.update({ent2id[ent]: class2id[concept]})
        else:
            entid2classid.update({ent2id[ent]: -1})
    return entid2classid


def init_workdir(work_dir):
    out_path = Path(work_dir)
    if not out_path.exists():
        out_path.mkdir(exist_ok=False)

class PatternScanner(ABC):

    @abstractmethod
    def pattern_to_int(self, file_entry):
        pass

    @abstractmethod
    def scan_pattern_df_rel(self, aggregated_triples):
        pass


class ContextResources:
    def __init__(self, original_hrt_triple_file_path, work_dir, create_id_file=False):
        init_workdir(work_dir)
         # h, r, t
        all_triples = read_original_hrt_triples_to_list(original_hrt_triple_file_path)
        self.ent2id, self.rel2id, self.hrt_int_df = hrt_original2int(all_triples,
                                                                     f"{work_dir}train/",
                                                                     create_id_file=create_id_file)
        self.hrt_to_scan_df = self.hrt_int_df
        self.class2id = class2id(ALL_CLASS_FILE)
        self.op2id = op2id(ALL_OP_FILE, self.rel2id)
        self.entid2classid = entid2classid_nell(self.ent2id, self.class2id)
        self.id2ent = {self.ent2id[key]: key for key in self.ent2id}
        self.id2rel = {self.rel2id[key]: key for key in self.rel2id}


def test():
    with open("../resources/NELL-995/entity2id.txt") as f:
        lines = f.readlines()[1:]
        all_d = []
        for l in lines:
            i = l.split('\t')
            all_d.append([i[0], int(i[1].strip())])
        all_d.sort(key=lambda x: x[1])
        print(len(all_d))




if __name__ == "__main__":
    # test()
    # read_hrt_original_2_hrt_rumis("../resources/NELL-995/NELLKG0.txt", "../outputs/rumis/ideal.data.txt")
    # read_hrt_rumis_2_hrt_int_df("../outputs/rumis/DLV/extension.opm.kg.pos.10.needcheck")
    # ot = read_original_hrt_triples("../resources/NELL-995/NELLKG0.txt")
    # hrt_original2int(ot, "../outputs/train/")
    # hrtdf = read_hrt_2_df("../outputs/valid_hrt.txt")
    # hrtdf2 = read_hrts_2_hrt_df("../outputs/transE_hrts.txt")
    # hrt_df2htr_transE(hrtdf, "../outputs/test1.txt")
    # hrtdf3 = read_htr_transE_2_hrt_df("../outputs/test1.txt")
    # read_hrt2htr_transE("../outputs/valid_hrt.txt", "../outputs/test3.txt")
    print("test done")
