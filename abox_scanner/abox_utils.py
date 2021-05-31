from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


def filter_overlap():
    pass


def set_operation():
    pass


def filter_valid_triples():
    pass


# NELL h, r, t
def read_all_triples(in_path):
    hrt_triples = []
    with open(in_path) as f:
        lines = f.readlines()
        for l in lines:
            items = l.split('\t')
            head = items[0].strip()
            tail = items[2].strip()
            rel = items[1].strip()
            hrt_triples.append([head, rel, tail])
    hrt_triples.sort(key=lambda x: x[1])
    return hrt_triples


#   input the ABox
#   return relation2id.txt, entity2id and instance2ids
def hrt_triples2int(hrt_triples, out_path):
    entities = set()
    relations = set()
    for l in hrt_triples:
        entities.add(l[0])
        entities.add(l[2])
        relations.add(l[1])
    entities = sorted(list(entities))
    relations = sorted(list(relations))
    entity2id = {e: e_idx for e_idx, e in enumerate(entities)}
    entity_total = len(entity2id)
    r_idx = entity_total
    rel2id = dict()
    for r in relations:
        if r not in entity2id:
            rel2id.update({r: r_idx})
            r_idx += 1
        else:
            rel2id.update({r: entity2id[r]})
    hrt_int = [[entity2id[tri[0]], rel2id[tri[1]], entity2id[tri[2]]] for tri in hrt_triples]
    # htr_new_lines = ''.join([f"{tri[0]} {tri[2]} {tri[1]}\n" for tri in hrt_int])
    # htr_new_lines = f"{len(hrt_int)}\n" + htr_new_lines
    # save_file(htr_new_lines, out_path + "/train2id.txt")
    ent2id_lines = ''.join([f"{ent}\t{id}\n" for ent, id in entity2id.items()])
    ent2id_lines = f"{len(entity2id)}\n" + ent2id_lines
    save_file(ent2id_lines, out_path + "/entity2id.txt")
    rel2id_lines = ''.join([f"{rel}\t{id}\n" for rel, id in rel2id.items()])
    rel2id_lines = f"{len(rel2id)}\n" + rel2id_lines
    save_file(rel2id_lines, out_path + "/relation2id.txt")
    id_dict = dict()
    id_dict.update(entity2id)
    id_dict.update({key: value for key, value in rel2id.items() if key not in entity2id})
    return id_dict, hrt_int


def hrt_transE2rht_transE(hrt_triples_file, rht_triples_file):
    df = pd.read_fwf(
        hrt_triples_file, header=None, columns=['head', 'rel', 'tail', 'score'])
    count = df.count()
    df2 = pd.concat([pd.DataFrame([count, '', '']), df], ignore_index=True)
    df2[['head', 'tail', 'rel']].to_csv(rht_triples_file, header=None, index=None)



def hrt2htr_transE(hrt_triples_file, rht_triples_file):
    df = pd.read_fwf(
        hrt_triples_file, header=None, columns=['head', 'rel', 'tail'])
    count = df.count()
    df2 = pd.concat([pd.DataFrame([count, '', '']), df], ignore_index=True)
    df2[['head', 'tail', 'rel']].to_csv(rht_triples_file, header=None, index=None)


def hrt_df2htr_transE(hrt_df, transE_train_file):
    count = hrt_df.count()
    df2 = pd.concat([pd.DataFrame([count, '', '']), hrt_df], ignore_index=True)
    df2[['head', 'tail', 'rel']].to_csv(transE_train_file, header=None, index=None)


def read_hrt_2_df(hrt_triples_file):
    df = pd.read_fwf(
        hrt_triples_file, header=None, columns=['head', 'rel', 'tail'])
    return df


def read_hrts_2_df(hrt_triples_file):
    df = pd.read_fwf(
        hrt_triples_file, header=None, columns=['head', 'rel', 'tail', 'score'])
    return df[['head', 'rel', 'tail']]


def read_htr_train_2_hrt_df(htr_with_count_file):
    df = pd.read_fwf(
        htr_with_count_file, header=None, columns=['head', 'tail', 'rel'])
    count = df.loc[0, 'head']
    df = df.iloc[1:]
    return count, df



def class2int(class_input, id_dict):
    class2id = dict()
    with open(class_input) as f:
        lines = f.readlines()
        id_count = len(id_dict)
        for l in lines:
            class_short = l.strip()
            if class_short not in id_dict:
                class2id.update({class_short: id_count})
                id_count += 1
            else:
                class2id.update({class_short: id_dict[class_short]})
    return class2id


def save_file(text, out_filename):
    out_path = Path(out_filename)
    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=False)
    with open(out_path, encoding='utf-8', mode='w') as out_f:
        out_f.write(text)
    out_f.close()


def nodeid2classid_nell(id_dict, class2id):
    nodeid2classid = dict()
    for node in id_dict:
        concept = node.split('_', 1)[0]
        if concept in class2id:
            nodeid2classid.update({id_dict[node]: class2id[concept]})
        else:
            nodeid2classid.update({id_dict[node]: -1})
    return nodeid2classid


class PatternScanner(ABC):

    @abstractmethod
    def pattern_to_int(self, file_entry):
        pass


    @abstractmethod
    def scan_pattern_df_rel(self, aggregated_triples):
        pass
