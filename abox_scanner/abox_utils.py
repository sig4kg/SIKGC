from __future__ import annotations
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from module_utils.file_util import *

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


def hrt_original2int(hrt_triples, out_dir, create_id_file=False):
    ent2id = dict()
    rel2id = dict()
    e_id = 0
    r_id = 0
    hrt_int = []
    for tri in tqdm(hrt_triples, desc="Converting triples to int ids..."):
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
        # save_to_file(htr_new_lines, out_dir + "/train2id.txt")
        ent2id_lines = ''.join([f"{ent}\t{id}\n" for ent, id in ent2id.items()])
        ent2id_lines = f"{len(ent2id)}\n" + ent2id_lines
        save_to_file(ent2id_lines, out_dir + "/entity2id.txt")
        rel2id_lines = ''.join([f"{rel}\t{id}\n" for rel, id in rel2id.items()])
        rel2id_lines = f"{len(rel2id)}\n" + rel2id_lines
        save_to_file(rel2id_lines, out_dir + "/relation2id.txt")
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


def entid2classid(ent2id, class2id, ent2type_file):
    ent2classes = dict()
    with open(ent2type_file) as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split('\t')
            if len(items) < 2:
                ent2classes.update({items[0]: ""})
            else:
                ent = items[0]
                classes = items[1].split(';')
                ent2classes.update({ent: classes})
    entid2classids = dict()
    for ent in tqdm(ent2id, desc="reading entity classes..."):
        concept_int = []
        if ent in ent2classes:
            concepts = ent2classes[ent]
            for concept in concepts:
                if concept in class2id:
                    concept_int.append(class2id[concept])
        if len(concept_int) > 0:
            entid2classids.update({ent2id[ent]: concept_int})
        else:
            entid2classids.update({ent2id[ent]: [-1]})
    return entid2classids


if __name__ == "__main__":
    print("test done")
