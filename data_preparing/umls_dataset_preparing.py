import types
import pandas as pd
from owlready2 import *


prefix = "http://umls.org/onto.owl"
#
# def add_objectproperty(ent_instance, property_name, property_value: []):
#     properties = dir(ent_instance)
#     if property_name not in properties:
#         setattr(ent_instance, property_name, property_value)
#     else:
#         attr = getattr(ent_instance, property_name)
#         for p in property_value:
#             if p not in attr:
#                 attr.append(p)
#         # setattr(ent_instance, property_name, attr)
#
#
# def exist_property(ent_instance, property_name):
#     properties = dir(ent_instance)
#     if property_name in properties:
#         return True
#     else:
#         return False
#
#
# def exist_property_and_value(ent_instance, property_name, property_value):
#     properties = dir(ent_instance)
#     if property_name in properties:
#         attr = getattr(ent_instance, property_name)
#         if property_value in attr:
#             return True


def read_tbox_rrf(rrf_file):
    chunk = {}
    list_of_chunk = []
    with open(rrf_file, 'r') as f:
        lines = f.readlines()
        HL_signal = False
        HL = []
        STL_signal = False
        STL = []
        for line in lines:
            if line == "\n":  # new chunk
                if len(HL) > 0:
                    chunk.update({'HL': HL})
                if len(STL) > 0:
                    chunk.update({'STL': STL})
                if len(chunk) > 0:
                    list_of_chunk.append(chunk)
                    chunk = {}
                    HL_signal = False
                    HL = []
                    STL_signal = False
                    STL = []
                continue
            key_value = line.strip().split(': ')
            if len(key_value) == 2:
                if key_value[0] in ['UI', 'STY', 'RL', 'RIN']:
                    chunk.update({key_value[0]: key_value[1]})
                elif key_value[0] == 'HL' and key_value[1] != '<none>':
                    HL_signal = True
                    STL_signal = False
                    HL.append(key_value[1].replace(';', ''))
                elif key_value[0] == 'STL' and key_value[1] != '<none>':
                    STL_signal = True
                    HL_signal = False
                    STL.append(key_value[1][1:-1].replace(';', '').replace(']', ''))
            elif len(key_value) == 1 and HL_signal is True:
                HL.append(key_value[0].replace(';', ''))
            elif len(key_value) == 1 and STL_signal is True:
                STL.append(key_value[0][1:-1].replace(';', '').replace(']', ''))
    return list_of_chunk


def read_groups(group_file):
    df = pd.read_csv(
        group_file, header=None, names=['brief', 'group_name', 'class_id', 'class_name'], sep="|")
    groups = df.groupby(['brief', 'group_name'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    group2clz = dict()
    group2name = dict()
    for idx, gp in groups.iterrows():
        group2clz.update({gp['brief']: gp['class_name']})
        group2name.update({gp['brief']: gp['group_name']})
    return group2clz


def convert_tbox(SU_chunks_dict_list, group2clz, work_dir):
    onto = get_ontology(prefix)
    text2Obj = {}
    ent_iri2text = {}
    rel_iri2text = {}
    ent2types = {}
    id2Obj = {}
    with onto:
        # add all classes and properties
        # for each class, we create an entity with same_name
        for chunk_dict in SU_chunks_dict_list:
            if 'RL' in chunk_dict:
                newProperty = types.new_class(chunk_dict['UI'], (ObjectProperty,))
                rel_iri2text.update({newProperty.iri: chunk_dict['RL']})
                text2Obj.update({chunk_dict['RL']: newProperty})
                id2Obj.update({chunk_dict['UI']: newProperty})
            elif 'STY' in chunk_dict:
                class_name = chunk_dict['UI']
                newClz = types.new_class(class_name, (Thing, ))
                text2Obj.update({chunk_dict['STY']: newClz})
                # a class is a class of itself
                ent2types.update({newClz.iri: [newClz.iri]})
                ent_iri2text.update({newClz.iri: chunk_dict['STY']})
                id2Obj.update({chunk_dict['UI']: newClz})
        # add subclasses, subproperties, inverse properties, domains, ranges
        for chunk_dict in SU_chunks_dict_list:
            if 'RL' in chunk_dict:
                if 'RIN' in chunk_dict:
                    # inverse property
                    RIN = chunk_dict['RIN']
                    r = text2Obj[chunk_dict['RL']]
                    if RIN in text2Obj:
                        inv_r = text2Obj[chunk_dict['RIN']]
                        r.inverse_property = inv_r
                    else:
                        inv_ui = 'inv_' + chunk_dict['UI']
                        invProperty = types.new_class(inv_ui, (ObjectProperty,))
                        r.inverse_property = invProperty
                        rel_iri2text.update({invProperty.iri: RIN})
                if 'HL' in chunk_dict:
                    # subproperty
                    for hl in chunk_dict['HL']:
                        hl_items = hl.split('} ')
                        if hl_items[0][1:] == 'isa':
                            sup = hl_items[1]
                            if sup in text2Obj:
                                r.is_a.append(text2Obj[sup])
                            else:
                                supProperty = types.new_class(sup, (ObjectProperty, ))
                                r.is_a.append(supProperty)
                                text2Obj.update({sub: supProperty})
                                rel_iri2text.update({supProperty.iri: sup})
                        elif hl_items[0][1:] == 'inverse_isa':
                            sub = hl_items[1]
                            if sub in text2Obj:
                                text2Obj[sub].is_a.append(r)
                            else:
                                subProperty = types.new_class(sub, (ObjectProperty))
                                subProperty.is_a.append(r)
                                text2Obj.update({sub: subProperty})
                                rel_iri2text.update({subProperty.iri: sub})
                if 'STL' in chunk_dict:
                    # create domain and range
                    heads = []
                    tails = []
                    for h_t in chunk_dict['STL']:
                        ht = h_t.split('|')
                        heads.append(ht[0])
                        tails.append(ht[1])
                    domain = types.new_class(chunk_dict['UI'] + '_domain', (Thing, ))
                    range = types.new_class(chunk_dict['UI'] + '_range', (Thing, ))
                    r.domain.append(domain)
                    r.range.append(range)
                    for h in heads:
                        text2Obj[h].is_a.append(domain)
                    for t in tails:
                        text2Obj[t].is_a.append(range)
            elif 'STY' in chunk_dict and 'HL' in chunk_dict:
                # subclasses
                this_class = text2Obj[chunk_dict['STY']]
                for hl in chunk_dict['HL']:
                    hl_items = hl.split('} ')
                    if hl_items[0][1:] == 'isa':
                        sup = hl_items[1]
                        if sup in text2Obj:
                            this_class.is_a.append(text2Obj[sup])
                        else:
                            supClass = types.new_class(sup, (Thing,))
                            this_class.is_a.append(text2Obj[sup])
                            text2Obj.update({sup: supClass})
                        ent2types[this_class.iri].append(text2Obj[sup].iri)
                    elif hl_items[0][1:] == 'inverse_isa':
                        sub = hl_items[1]
                        if sub in text2Obj:
                            text2Obj[sub].is_a.append(this_class)
                        else:
                            sub_class = types.new_class(sub, (Thing))
                            sub_class.is_a.append(this_class)
                            text2Obj.update({sub: sub_class})
                        ent2types[text2Obj[sub].iri].append(this_class.iri)
        # add group and disjointness
        disjoint_groups = []
        for sup, subs in group2clz.items():
            sup_class = types.new_class(sup, (Thing,))
            disjoint_groups.append(sup_class)
            text2Obj.update({sup: sup_class})
            for sub in subs:
                text2Obj[sub].is_a.append(sup_class)
        AllDisjoint(disjoint_groups)
        # save TBox
        onto.save(file = work_dir + "tbox1.nt", format="ntriples")
        # with open(work_dir + 'ent2types.txt', 'w') as f:
        #     for ent, clz in ent2types.items():
        #         f.write(f"{ent}\t{';'.join(list(set(clz)))}\n")
        with open(work_dir + 'entity2text1.txt', 'w') as f:
            for ent, text in ent_iri2text.items():
                f.write(f"{ent}\t{text}\n")
        with open(work_dir + 'relation2text.txt', 'w') as f:
            for rel, text in rel_iri2text.items():
                f.write(f"{rel}\t{text}\n")
        return text2Obj, id2Obj


def convert_rel_assertions_tbox(text2Obj, SU_chunks_dict_list, work_dir):
    # add namedIndividual and relational assertions
    rel_triples = []
    for chunk_dict in SU_chunks_dict_list:
        if 'RL' in chunk_dict and 'STL' in chunk_dict:
            rel_uri = text2Obj[chunk_dict['RL']].iri
            for h_t in chunk_dict['STL']:
                ht = h_t.split('|')
                h = ht[0]
                t = ht[1]
                h_ent = text2Obj[h].iri
                t_ent = text2Obj[t].iri
                rel_triples.append(f"<{h_ent}> <{rel_uri}> <{t_ent}> .\n")
    with open(work_dir + 'tbox2.nt', 'w') as f:
        f.writelines(rel_triples)


def convert_rel_assertions(rel_file, id2tbox_obj, work_dir):
    pd_rel1 = pd.read_csv(rel_file, header=None, names=[i for i in range(14)], sep="|", error_bad_lines=False, engine="python")
    pd_hrt_id = pd_rel1[[0,8,4]].drop_duplicates(keep='first')
    triples = []
    for idx, row in pd_hrt_id:
        h_id = row[0]
        r_id = row[8]
        t_id = row[4]
        triples.append(f"<{prefix}/{h_id}> <{id2tbox_obj[r_id].iri}> {prefix}/{t_id}>")
        with open(work_dir + 'abox.nt', 'w') as f:
            f.writelines(triples)


def convert_cid2name(ent_file, work_dir):
    pd_ent_and_names = pd.read_csv(ent_file, header=None, names=[i for i in range(18)], sep="|", error_bad_lines=False, engine="python")
    pd_ent_names = pd_ent_and_names.query("1==ENG")[[0, 1, 14]].drop_duplicates(subset=[0], keep='first')
    del pd_ent_and_names
    cid2name = dict()
    for idx, row in pd_ent_names.iterrows():
        cid = row[0]
        name = row[14]
        cid2name.update({cid: name})
    with open(work_dir + "entity2text2.txt", 'w') as f:
        for ent, text in cid2name.items():
            f.write(f"{prefix}/{ent}\t{text}\n")


def convert_type_assertions(type_file, id2tbox_obj, work_dir):
    pd_ent_and_types = pd.read_csv(type_file, header=None, names=[i for i in range(6)], sep="\t", error_bad_lines=False, engine="python")
    pd_ent_type = pd_ent_and_types[[0, 1]].groupby([0], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    del pd_ent_and_types
    cid2obj_iris = dict()
    for idx, row in pd_ent_type:
        cid = row[0]
        tid = row[1]
        if cid not in cid2obj_iris:
            cid2obj_iris.update({cid: [id2tbox_obj[tid].iri]})
        else:
            cid2obj_iris[cid].append(id2tbox_obj[tid].iri)
    with open(work_dir + "entity2type.txt", 'w') as f:
        for ent, ts in cid2obj_iris.items():
            f.write(f"{prefix}/{ent}\t{';'.join(ts)}\n")


if __name__ == "__main__":
    wdir = "../resources/UMLS/"
    gp2clz = read_groups("../resources/UMLS/SemGroups.txt")
    tmp_chunks = read_tbox_rrf("../resources/UMLS/SU")
    phrase2obj, tid2obj = convert_tbox(tmp_chunks, gp2clz, wdir)
    convert_rel_assertions_tbox(phrase2obj, tmp_chunks, wdir)
    convert_cid2name("../resources/UMLS/MRCONSO.RRF", wdir)
    convert_type_assertions("../resources/UMLS/MRSTY.RRF", tid2obj, wdir)
    convert_rel_assertions("../resources/UMLS/MRREL.RRF", tid2obj, wdir)
