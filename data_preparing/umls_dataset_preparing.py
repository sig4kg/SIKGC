import types

from owlready2 import *

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
            if line == "":  # new chunk
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
                elif key_value[0] is 'HL':
                    HL_signal = True
                    STL_signal = False
                    HL.append(key_value[1][:-1])
                elif key_value[0] is 'STL':
                    STL_signal = True
                    HL_signal = False
                    STL.append(key_value[1][:-1])
            elif len(key_value) == 1 and HL_signal is True:
                HL.append(key_value[:-1])
            elif len(key_value) == 1 and STL_signal is True:
                STL.append(key_value[:-1])


def convert_tbox(SU_chunks_dict_list, work_dir):
    onto = get_ontology("http://umls.org/onto.owl")
    text2rel = {}
    text2Obj = {}
    text2ent = {}
    with onto:
        # add all classes and properties
        # for each class, we create an entity with same_name
        for chunk_dict in SU_chunks_dict_list:
            if 'RL' in chunk_dict:
                newProperty = types.new_class(chunk_dict['UI'], ObjectProperty)
                text2ent.update({chunk_dict['RL']: chunk_dict['UI']})
                text2Obj.update({chunk_dict['RL']: newProperty})
            elif 'STY' in chunk_dict:
                class_name = chunk_dict['UI'] + '_T'
                newClz = types.new_class(class_name, Thing)
                text2Obj.update({chunk_dict['STY']: newClz})
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
                        text2rel.update({RIN: inv_ui})
                        invProperty = types.new_class(inv_ui, ObjectProperty)
                        r.inverse_property = invProperty
                if 'HL' in chunk_dict:
                    # subproperty
                    for hl in chunk_dict['HL']:
                        hl_items = hl.split('} ')
                        if hl_items[0][1:] is 'isa':
                            sup = hl_items[1]
                            if sup in text2Obj:
                                text2Obj[sup].subproperties.append(r)
                            else:
                                supProperty = types.new_class(sup, ObjectProperty)
                                text2rel.update({sup: sup})
                                supProperty.subproperties = [r]
                                text2Obj.update({sub: supProperty})
                        elif hl_items[0][1:] is 'inverse_isa':
                            sub = hl_items[1]
                            if sub in text2Obj:
                                r.subproperties.append(text2Obj[sub])
                            else:
                                subProperty = types.new_class(sub)
                                r.subproperties.append(subProperty)
                                text2rel.update({sub: sub})
                                text2Obj.update({sub: subProperty})
                if 'STL' in chunk_dict:
                    # create domain and range
                    heads = []
                    tails = []
                    for h_t in chunk_dict['STL']:
                        ht = h_t.split('|')
                        heads.append(ht[0][1:])
                        tails.append(ht[1][:-1])
                    domain = types.new_class(chunk_dict['UI'] + '_domain', Thing)
                    range = types.new_class(chunk_dict['UI'] + '_range', Thing)
                    for h in heads:
                        text2Obj[h].is_a.append(domain)
                    for t in tails:
                        text2Obj[t].is_a.append(range)
            elif 'STY' in chunk_dict and 'HL' in chunk_dict:
                # subclasses
                this_class = text2Obj[chunk_dict['STY']]
                for hl in chunk_dict['HL']:
                    hl_items = hl.split('} ')
                    if hl_items[0][1:] is 'isa':
                        sup = hl_items[1]
                        if sup in text2Obj:
                            this_class.is_a.append(text2Obj[sup])
                        else:
                            supClass = types.new_class(sup + '_T', Thing)
                            this_class.is_a.append(text2Obj[sup])
                            text2Obj.update({sup: supClass})
                    elif hl_items[0][1:] is 'inverse_isa':
                        sub = hl_items[1]
                        if sub in text2Obj:
                            text2Obj[sub].is_a.append(this_class)
                        else:
                            sub_class = types.new_class(sub)
                            sub_class.is_a.append(this_class)
                            text2Obj.update({sub: sub_class})
        # save TBox
        onto.save(file = work_dir + "tbox.nt", format="ntriples")


def convert_abox(text2Obj, text2UI, SU_chunks_dict_list, work_dir):
    # add namedIndividual and relational assertions
    text2ent = {}
    rel_triples = []
    type_triples = []
    named_individual = ""
    typeof = ""
    prefix = ""
    for chunk_dict in SU_chunks_dict_list:
        if 'RL' in chunk_dict and 'STL' in chunk_dict:
            rel_uri = text2Obj[chunk_dict['RL']].iri.to_string()
            for h_t in chunk_dict['STL']:
                ht = h_t.split('|')
                h = ht[0][1:]
                t = ht[1][:-1]
                if h in text2ent:
                    h_ent = text2ent[h]
                else:
                    h_class = text2Obj[h]
                    h_ent = h_class(text2UI[h])
                    text2ent.update({h: h_ent})
                    type_triples.append(f"<{prefix}{text2UI[h]}> <{typeof}> <{named_individual}> .")
                    type_triples.append(f"<{prefix}{text2UI[h]}> <{typeof}> <{h_class.iri.to_string()}> .")
                if t in text2ent:
                    t_ent = text2ent[t]
                else:
                    t_class = text2Obj[t]
                    t_ent = t_class(text2UI[t])
                    text2ent.update({t: t_ent})
                    type_triples.append(f"<{prefix}{text2UI[t]}> <{typeof}> <{named_individual}> .")
                    type_triples.append(f"<{prefix}{text2UI[t]}> <{typeof}> <{t_class.iri.to_string()}> .")
                rel_triples.append(f"<{prefix}{text2UI[h]}> <{rel_uri}> <{prefix}{text2UI[t]}>")















def convert_types(rrf_file, work_dir):
    pass


def convert_text(rrf_file, work_dir):
    pass


def convert_abox(rrf_file, work_dir):
    pass


if __name__ == "__main__":
    format_nt("../resources/DB15K/DB15K_EntityTriples.nt", "../resources/DB15K/")
    # get_types("../resources/DB15K/DB15K_EntityTriples.txt", "../resources/DB15K/")
    # get_dict_and_save("../resources/DB15K/DB15K_EntityTriples.txt")
    # get_rel_dict_and_save("../resources/DB15K/DB15K_EntityTriples.txt", "../resources/DB15K/rel2wikiid.pkl",  ' ')
    # get_all_classes_relations("../resources/DB15K/entity2type.txt",
    #                           "../resources/DB15K/DB15K_EntityTriples.txt",
    #                           "../outputs/db15k/")
    # get_negations("../resources/DB15K/neg_statistical_inference.tsv", "../resources/DB15K/")
    # get_rel_dict_and_save("../resources/DBpedia-politics/abox_hrt_uri.txt", "../resources/DBpedia-politics/rel2wikiid.pkl",  '\t')
    # get_ent_dict_and_save2("../resources/DBpedia-politics/abox_hrt_uri.txt", "../resources/DBpedia-politics/ent2wikiid.pkl", '\t')
