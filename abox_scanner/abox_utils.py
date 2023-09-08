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


def hrt_original2int(hrt_triples, op2id: dict, class2id: dict):
    ent2id = dict()
    e_id = len(class2id) - 1
    r_id = len(op2id)
    hrt_int = []
    for tri in tqdm(hrt_triples, desc="Converting triples to int ids..."):
        if tri[0] not in ent2id:
            ent2id.update({tri[0]: e_id})
            e_id += 1
        if tri[2] not in ent2id:
            ent2id.update({tri[2]: e_id})
            e_id += 1
        if tri[1] not in op2id:
            op2id.update({tri[1]: r_id})
            r_id += 1
        hrt_int.append([ent2id[tri[0]], op2id[tri[1]], ent2id[tri[2]]])
    hrt_int_df = pd.DataFrame(data=hrt_int, columns=['head', 'rel', 'tail']).drop_duplicates(keep='first')
    return ent2id, hrt_int_df


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


def op2id(op_file):
    op2id = dict()
    with open(op_file) as f:
        lines = f.readlines()
        idx = 1
        for l in lines:
            ls = l.strip()
            op2id.update({ls: idx})
            idx += 1
    op2id.update({"http://www.w3.org/1999/02/22-rdf-syntax-ns#type": 0})
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
            entid2classids.update({ent2id[ent]: []})
    return entid2classids


if __name__ == "__main__":
    print("test done")
