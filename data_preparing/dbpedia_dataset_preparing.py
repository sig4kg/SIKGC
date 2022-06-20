from collections import Counter
from pathlib import Path
import platform
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
import time
import pandas as pd
from abox_scanner import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources


# DEFAULT_GRAPH = "http://dbpedia.org"
TYPE_OF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
WIKIPAGE_REDIRECTS = "http://dbpedia.org/ontology/wikiPageRedirects"
COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"
DISAMBIGUATE = "http://dbpedia.org/ontology/wikiPageDisambiguates"
LOCALHOST = "localhost"
DBPEDIA_GRAPH_PORT = 8890 if platform.system() == 'Linux' else 5002
DBPEDIA_GRAPH_URL = f"http://{LOCALHOST}:{DBPEDIA_GRAPH_PORT}/sparql"


def get_query_values(query_str):
    sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL)
    sparql.setTimeout(20)
    sparql.setQuery(query_str)
    sparql.setReturnFormat(JSON)
    values = []
    try:
        response = sparql.query()
        results = response.convert()
        for record in results["results"]["bindings"]:
            if 'xml:lang' in record['object'] and record['object']['xml:lang'] != 'en':
                continue
            entity_class = record['object']['value']
            values.append(entity_class)
        response.response.close()
        return values
    except Exception as err:
        print("failed to query dbpedia virtuoso...")
        return values


def get_classes(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "WHERE {" \
        f"<{resource_uri}> <{TYPE_OF}> ?object . " \
        "} LIMIT 500"
    all_classes = get_query_values(query_str)
    return all_classes


def get_classes_redirected(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "WHERE {" \
        f"<{resource_uri}> <{WIKIPAGE_REDIRECTS}> ?x . " \
        f"?x <{TYPE_OF}> ?object . " \
        "} LIMIT 500"
    all_classes = get_query_values(query_str)
    return all_classes


def get_long_text(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "WHERE {" \
        f"<{resource_uri}> <{COMMENT}> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def get_long_text_redirected(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "WHERE {" \
        f"<{resource_uri}> <{WIKIPAGE_REDIRECTS}> ?x . " \
        f"?x <{COMMENT}> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def get_short_text(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "WHERE {" \
        f"<{resource_uri}> <http://www.w3.org/2000/01/rdf-schema#label> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def query_rel_text(rel_file, work_dir):
    rel2shorttext_l = []
    with open(rel_file) as f:
        lines = f.readlines()
        rel_lines = lines[1:]
        for rel in tqdm(rel_lines):
            rel = rel.split('\t')[0]
            short_text = get_short_text(rel)
            if len(short_text) == 0:
                short_text = rel.split('/')[-1].replace('_', ' ')
            rel2shorttext_l.append(f"{rel}\t{short_text}")
    save_and_append_results(rel2shorttext_l, work_dir + "relation2text.txt")


def query_entity_text(entity_file, work_dir):
    no_long_text = []
    batch = 1000
    flush_num = batch
    ent2longtext_l = []
    ent2shorttext_l = []
    with open(entity_file) as f:
        lines = f.readlines()
        count = int(lines[0].strip())
        entity_lines = lines[1:]
        with tqdm(total=len(entity_lines), desc=f"preparing dbpedia data...") as pbar:
            for idx, l in enumerate(lines[1:]):
                items = l.split('\t')
                entity_iri = items[0]
                long_text = get_long_text(entity_iri)
                if len(long_text) == 0:
                    no_long_text.append(entity_iri)
                else:
                    ent2longtext_l.append(f"{entity_iri}\t{long_text}")
                short_text = get_short_text(entity_iri)
                if len(short_text) == 0:
                    short_text = entity_iri.split('/')[-1].replace('_', ' ')
                ent2shorttext_l.append(f"{entity_iri}\t{short_text}")
                flush_num -= 1
                pbar.update(1)
                if flush_num == 0 or idx == count - 1:
                    save_and_append_results(ent2longtext_l, work_dir + "entity2textlong.txt")
                    save_and_append_results(ent2shorttext_l, work_dir + "entity2text.txt")
                    flush_num = batch
                    ent2longtext_l = []
    save_and_append_results(no_long_text, work_dir + "no_long_text.txt")
    print("done")


def query_wiki_redirect_type(entities):
    no_class = []
    ent2classes_l = []
    for ent in tqdm(entities):
        ent = ent.strip()
        classes = get_classes_redirected(ent)
        if len(classes) == 0:
            no_class.append(ent)
        else:
            classes = list(set(classes))
            classes = [clz for clz in classes if "http://dbpedia.org/class/yago/" not in clz
                       and "http://www.ontologydesignpatterns.org/" not in clz and "http://www.wikidata.org/" not in clz]
            ent2classes_l.append((ent, list(set(classes))))
    return ent2classes_l, no_class


def query_wiki_redirect_text(entities):
    no_long_text = []
    ent2longtext_l = []
    for ent in tqdm(entities):
        ent = ent.strip()
        long_text = get_long_text_redirected(ent)
        if len(long_text) == 0:
            no_long_text.append(ent)
        else:
            ent2longtext_l.append(f"{ent}\t" + long_text)
    print("done")
    return ent2longtext_l, no_long_text


def query_disambiguration_type(all_triples, all_no_class_ents):
    no_class = []
    ent2classes_l = []
    for ent in tqdm(all_no_class_ents):
        triples = list(filter(lambda x: ent in x, all_triples))
        found = False
        for tri in triples:
            tri_hrt = tri
            query_clause = f"<{tri_hrt[0]}> <{tri_hrt[1]}> <{tri_hrt[2]}>"
            query_clause = query_clause.replace(f"<{ent}>", "?x")
            query_str = f"SELECT distinct ?object " \
                "WHERE {" \
                f"<{ent}> <{DISAMBIGUATE}> ?x . " \
                f"{query_clause} . " \
                f"?x <{TYPE_OF}> ?object . " \
                "} LIMIT 500"
            classes = get_query_values(query_str)
            if len(classes) == 0:
                continue
            else:
                classes = list(set(classes))
                classes = [clz for clz in classes if "http://dbpedia.org/class/yago/" not in clz
                           and "http://www.ontologydesignpatterns.org/" not in clz and "http://www.wikidata.org/" not in clz]
                ent2classes_l.append((ent, list(set(classes))))
                found = True
                break
        if not found:
            no_class.append(ent)
    return ent2classes_l, no_class


def query_disambiguration_text(all_triples, all_no_longtext_ents, work_dir):
    no_long_text = []
    ent2longtext_l = []
    for ent in tqdm(all_no_longtext_ents):
        ent = ent.strip()
        triples = list(filter(lambda x: ent in x, all_triples))
        found = False
        for tri in triples:
            tri_hrt = tri
            query_clause = f"<{tri_hrt[0]}> <{tri_hrt[1]}> <{tri_hrt[2]}>"
            query_clause = query_clause.replace(f"<{ent}>", "?x")
            query_str = f"SELECT distinct ?object " \
                "WHERE {" \
                f"<{ent}> <{DISAMBIGUATE}> ?x . " \
                f"{query_clause} . " \
                f"?x <{COMMENT}> ?object . " \
                "} LIMIT 500"
            long_text = get_query_values(query_str)
            if len(long_text) == 0:
                continue
            else:
                ent2longtext_l.append(f"{ent}\t" + long_text[0])
                found = True
        if not found:
            no_long_text.append(ent)
    save_and_append_results(ent2longtext_l, work_dir + "entity2textlong_disambigurate.txt")
    save_and_append_results(no_long_text, work_dir + "no_long_text3.txt")
    print("done")


def get_triples_entities(triple_file):
    entities = set()
    all_triples = []
    with open(triple_file) as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split("\t")
            all_triples.append(items)
            entities.add(items[0])
            entities.add(items[2])
    return all_triples, list(entities)


def generate_entity2type(triple_file, work_dir):
    no_class = []
    batch = 1000
    flush_num = batch
    ent2classes_l = []
    all_triples, entities = get_triples_entities(triple_file)
    with tqdm(total=len(entities), desc=f"preparing dbpedia type data...") as pbar:
        for idx, ent in enumerate(entities):
            classes = get_classes(ent)
            classes = list(set(classes))
            classes = [clz for clz in classes if "http://dbpedia.org/class/yago/" not in clz
                       and "http://www.ontologydesignpatterns.org/" not in clz and "http://www.wikidata.org/" not in clz]

            if len(classes) == 0:
                print("query_disambiguration_type...")
                disamb, _ = query_disambiguration_type(all_triples, [ent])
                if len(disamb) > 0:
                    ent2classes_l.extend(disamb)
                else:
                    print("query_wiki_redirect_type...")
                    redirect, _ = query_wiki_redirect_type([ent])
                    if len(redirect) > 0:
                        ent2classes_l.extend(redirect)
                    else:
                        no_class.append(ent)
            else:
                ent2classes_l.append((ent, classes))
            flush_num -= 1
            pbar.update(1)
            if flush_num == 0 or idx == len(entities) - 1:
                save_and_append_results([f"{x[0]}\t{';'.join(x[1])}" for x in ent2classes_l], work_dir + "entity2type.txt")
                flush_num = batch
                ent2classes_l.clear()
    save_and_append_results(no_class, work_dir + "no_type.txt")


def entity_type_nt(entity2type_file, work_dir):
    type_nt = []
    with open(entity2type_file) as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split('\t')
            ent = items[0]
            classes = items[1].split(';')
            type_nt.extend([f"{ent}\t{TYPE_OF}\t{xx}\n" for xx in classes])
    save_and_append_results(type_nt, work_dir + "abox_type.nt")


def save_and_append_results(d_list, out_filename):
    out_file = Path(out_filename)
    if not out_file.parent.exists():
        out_file.parent.mkdir(exist_ok=False)

    with open(out_filename, encoding='utf-8', mode='a') as out_f:
        for item in d_list:
            out_f.write(item + '\n')
        out_f.close()


def get_all_classes_relations(entity2class_uri_file, hrt_uri_file, out_dir):
    df = pd.read_csv(hrt_uri_file, header=None, names=['head', 'rel', 'tail'], sep="\t", error_bad_lines=False, engine="python")
    df['rel'].drop_duplicates(keep="first").to_csv(out_dir + "properties.txt", header=False, index=False, mode='w')
    all_types = []
    with open(entity2class_uri_file) as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split('\t')
            classes = items[1].split(';')
            all_types.extend(classes)
    all_types = list(set(all_types))
    save_and_append_results(all_types, out_dir + "types.txt")


def fix_dbpedia_property_constraints():
    triples_path = "../resources/DBpediaP/PoliticalTriplesWD.txt"  # h, t, r
    class_and_op_file_path = "../resources/DBpedia-politics/"
    tbox_patterns_path = "../resources/DBpedia-politics/tbox_patterns/"
    to_fix_domain_properties = "../resources/DBpediaP/fixDomain.txt"
    to_fix_range_properties = "../resources/DBpediaP/fixRange.txt"
    work_dir = "../outputs/fixdata/"
    context_resources = ContextResources(triples_path, class_and_op_file_path= class_and_op_file_path, work_dir=work_dir, create_id_file=False)
    abox_scanner_scheduler = AboxScannerScheduler.AboxScannerScheduler(tbox_patterns_path, context_resources=context_resources)
    abox_scanner_scheduler.register_pattern([1, 2, 5,8,9,10,11,12,13], ['pos_domain', 'pos_range'] ) #, 5,8,9,10,11,12,13
    valids, invalids = abox_scanner_scheduler.scan_rel_IJPs(work_dir='../outputs/test/')
    context_resources.hrt_int_df = valids
    exclude_type = "http://www.w3.org/2002/07/owl#Thing"
    p2domain = {}
    with open(to_fix_domain_properties) as fd1:
        lines1 = fd1.readlines()
        not_found = []
        for p in lines1:
            p = p.strip()
            if p not in context_resources.rel2id:
                not_found.append(p)
                continue
            p_id = context_resources.rel2id[p]
            tris_p = context_resources.hrt_int_df.query("rel == @p_id")
            if len(tris_p.index) == 0:
                not_found.append(p)
                continue
            len_tris = len(tris_p.index)
            h_types = [t for h in tris_p['head'] for t in context_resources.entid2classids[h]]
            h_counter = Counter(h_types)
            found = False
            for a in h_counter.most_common():
                ta_count = a[1]
                ta = a[0]
                if ta == -1:
                    len_tris = len_tris - int(ta_count)
                    continue
                ta_uri = context_resources.classid2class[ta]
                if ta_uri == exclude_type or 'http://dbpedia.org/ontology/' not in ta_uri:
                    continue
                else:
                    rate = ta_count / len_tris
                    if rate >= 0.75:
                        p2domain.update({p: ta_uri})
                        found = True
                    break
            if not found:
                not_found.append(p)

    p2range = {}
    with open(to_fix_range_properties) as fd2:
        lines2 = fd2.readlines()
        not_found2 = []
        for p in lines2:
            p = p.strip()
            if p not in context_resources.rel2id:
                not_found2.append(p)
                continue
            p_id = context_resources.rel2id[p]
            tris_p = context_resources.hrt_int_df.query("rel == @p_id")
            if len(tris_p.index) == 0:
                not_found2.append(p)
                continue
            len_tris = len(tris_p.index)
            h_types = [t for h in tris_p['tail'] for t in context_resources.entid2classids[h]]
            h_counter = Counter(h_types)
            found = False
            for a in h_counter.most_common():
                ta_count = a[1]
                ta = a[0]
                if ta == -1:
                    len_tris = len_tris - 1
                    continue
                ta_uri = context_resources.classid2class[ta]
                if ta_uri == exclude_type or 'http://dbpedia.org/ontology/' not in ta_uri:
                    continue
                else:
                    rate = ta_count / len_tris
                    if rate > 0.75:
                        p2range.update({p: ta_uri})
                        found = True
                    break
            if not found:
                not_found2.append(p)

    all_pro = [k for k in p2domain.keys()]
    all_pro.extend([k for k in p2range.keys()])
    all_pro = list(set(all_pro))
    constrains = []
    for pp in all_pro:
        if pp in p2domain:
            row1 = f"<{pp}> <http://www.w3.org/2000/01/rdf-schema#domain> <{p2domain[pp]}> ."
            constrains.append(row1)
        if pp in p2range:
            row2 = f"<{pp}> <http://www.w3.org/2000/01/rdf-schema#range> <{p2range[pp]}> ."
            constrains.append(row2)
    save_and_append_results(constrains, work_dir + "fixed_uri.nt")


if __name__ == "__main__":
    # get_all_classes_relations("../resources/DBpedia-politics/entity2type.txt", "../resources/DBpedia-politics/PoliticalTriplesWD.txt", out_dir="../outputs/test_dbpedia/")
    # generate_entity2type("../resources/DBpediaP/PoliticalTriplesWD.txt", "../outputs/dbpedia_data/")
    pass