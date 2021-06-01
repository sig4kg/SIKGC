from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd



ONTOLOGY_PATH = "../resources/NELL.ontology.ttl"
TBOX_PATTERNS_PATH = "../resources/NELL_patterns"
ALL_CLASS_FILE = "../resources/NELL-995/ALLClasses.txt"
ALL_OP_FILE = "../resources/NELL-995/ALLObjectProperties.txt"
ORIGINAL_TRIPLES_PATH = "../resources/NELL-995/NELLKG0.txt"


# NELL h, r, t
def read_original_hrt_triples(in_path):
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
    if create_id_file:
        htr_new_lines = ''.join([f"{tri[0]} {tri[2]} {tri[1]}\n" for tri in hrt_int])
        htr_new_lines = f"{len(hrt_int)}\n" + htr_new_lines
        save_file(htr_new_lines, out_dir + "/train2id.txt")
        ent2id_lines = ''.join([f"{ent}\t{id}\n" for ent, id in ent2id.items()])
        ent2id_lines = f"{len(ent2id)}\n" + ent2id_lines
        save_file(ent2id_lines, out_dir + "/entity2id.txt")
        rel2id_lines = ''.join([f"{rel}\t{id}\n" for rel, id in rel2id.items()])
        rel2id_lines = f"{len(rel2id)}\n" + rel2id_lines
        save_file(rel2id_lines, out_dir + "/relation2id.txt")
    return ent2id, rel2id, hrt_int


def read_hrt_2_df(hrt_triples_file):
    df = pd.read_csv(
        hrt_triples_file, header=None, names=['head', 'rel', 'tail'], sep="\t")
    return df


def read_hrts_2_hrt_df(hrts_file):
    df = pd.read_csv(
        hrts_file, header=None, names=['head', 'rel', 'tail', 'score'], sep="\t")
    return df[['head', 'rel', 'tail']]


def read_htr_transE_2_hrt_df(htr_with_count_file):
    df = pd.read_csv(
        htr_with_count_file, header=None, names=['head', 'tail', 'rel'], dtype={'head':str, 'tail':str, 'rel':str}, sep="\t")
    count = int(df.loc[0, 'head'])
    df = df.iloc[1:]
    df.astype(int)
    return count, df


def hrt_df2htr_transE(hrt_df, transE_train_file):
    count = hrt_df.count()
    first_line_df = pd.DataFrame(data=[[count[0], '', '']], columns=['head', 'tail', 'rel'])
    df2 = pd.concat([first_line_df, hrt_df], 0)
    outfile = open(transE_train_file, 'wb')
    df2[['head', 'tail', 'rel']].to_csv(outfile, header=None, index=None, sep='\t')
    outfile.close() # wait until file is saved


def read_hrt2htr_transE(hrt_triples_file, transE_train_file):
    df = pd.read_csv(
        hrt_triples_file, header=None, names=['head', 'rel', 'tail'], sep='\t')
    hrt_df2htr_transE(df, transE_train_file)


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


def entid2classid_nell(ent2id, class2id):
    entid2classid = dict()
    for ent in ent2id:
        concept = ent.split('_', 1)[0]
        if concept in class2id:
            entid2classid.update({ent2id[ent]: class2id[concept]})
        else:
            entid2classid.update({ent2id[ent]: -1})
    return entid2classid


class PatternScanner(ABC):

    @abstractmethod
    def pattern_to_int(self, file_entry):
        pass

    @abstractmethod
    def scan_pattern_df_rel(self, aggregated_triples):
        pass


class ContextResources:
    def __init__(self, original_hrt_triple_file_path, work_dir, create_id_file=False):
         # h, r, t
        all_triples = read_original_hrt_triples(original_hrt_triple_file_path)
        self.ent2id, self.rel2id, self.hrt_tris_int = hrt_original2int(all_triples, f"{work_dir}train/", create_id_file=create_id_file)
        self.class2id = class2id(ALL_CLASS_FILE)
        self.op2id = op2id(ALL_OP_FILE, self.rel2id)
        self.entid2classid = entid2classid_nell(self.ent2id, self.class2id)


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
    ot = read_original_hrt_triples("../resources/NELL-995/NELLKG0.txt")
    hrt_original2int(ot, "../outputs/train/")
    # hrtdf = read_hrt_2_df("../outputs/valid_hrt.txt")
    # hrtdf2 = read_hrts_2_hrt_df("../outputs/transE_hrts.txt")
    # hrt_df2htr_transE(hrtdf, "../outputs/test1.txt")
    # hrtdf3 = read_htr_transE_2_hrt_df("../outputs/test1.txt")
    # read_hrt2htr_transE("../outputs/valid_hrt.txt", "../outputs/test3.txt")
    print("test done")
