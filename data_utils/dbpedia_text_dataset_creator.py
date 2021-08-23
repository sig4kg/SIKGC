from pathlib import Path
import platform
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm


DEFAULT_GRAPH = "http://dbpedia.org"
TYPE_OF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
WIKIPAGE_REDIRECTS = "http://dbpedia.org/ontology/wikiPageRedirects"
COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"
DISAMBIGUATE = "http://dbpedia.org/ontology/wikiPageDisambiguates"
LOCALHOST = "localhost"
DBPEDIA_GRAPH_PORT = 8890 if platform.system() == 'Linux' else 5002
DBPEDIA_GRAPH_URL = f"http://{LOCALHOST}:{DBPEDIA_GRAPH_PORT}/sparql"


def get_query_values(query_str):
    sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL, defaultGraph=DEFAULT_GRAPH)
    sparql.setTimeout(10)
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
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <{TYPE_OF}> ?object . " \
        "} LIMIT 500"
    all_classes = get_query_values(query_str)
    return all_classes


def get_classes_redirected(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <{WIKIPAGE_REDIRECTS}> ?x . " \
        f"?x <{TYPE_OF}> ?object . " \
        "} LIMIT 500"
    all_classes = get_query_values(query_str)
    return all_classes


def get_long_text(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <{COMMENT}> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def get_long_text_redirected(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <{WIKIPAGE_REDIRECTS}> ?x . " \
        f"?x <{COMMENT}> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def get_short_text(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <http://www.w3.org/2000/01/rdf-schema#label> ?object . " \
        "} LIMIT 500"
    text = get_query_values(query_str)
    text = text[0] if len(text) > 0 else ''
    return text


def query_entity_text_and_class(entity_file, work_dir):
    no_class = []
    no_long_text = []
    batch = 1000
    flush_num = batch
    ent2classes_l = []
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
                classes = get_classes(entity_iri)
                if len(classes) == 0:
                    no_class.append(entity_iri)
                else:
                    ent2classes_l.append(f"{entity_iri}\t" + ";".join(classes))
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
                    save_and_append_results(ent2classes_l, work_dir + "entity2type.txt")
                    save_and_append_results(ent2longtext_l, work_dir + "entity2textlong.txt")
                    save_and_append_results(ent2shorttext_l, work_dir + "entity2text.txt")
                    flush_num = batch
                    ent2classes_l = []
                    ent2longtext_l = []
    save_and_append_results(no_class, work_dir + "no_class.txt")
    save_and_append_results(no_long_text, work_dir + "no_long_text.txt")
    print("done")


def query_wiki_redirect(work_dir):
    no_class = []
    no_long_text = []
    ent2classes_l = []
    ent2longtext_l = []
    with open(work_dir + "no_class.txt") as f:
        lines = f.readlines()
        for ent in tqdm(lines):
            ent = ent.strip()
            classes = get_classes_redirected(ent)
            if len(classes) == 0:
                no_class.append(ent)
            else:
                ent2classes_l.append(f"{ent}\t" + ";".join(classes))
        save_and_append_results(ent2classes_l, work_dir + "entity2type_redirected.txt")
    with open(work_dir + "no_long_text.txt") as f:
        lines = f.readlines()
        for ent in tqdm(lines):
            ent = ent.strip()
            long_text = get_long_text_redirected(ent)
            if len(long_text) == 0:
                no_long_text.append(ent)
            else:
                ent2longtext_l.append(f"{ent}\t" + long_text)
        save_and_append_results(ent2longtext_l, work_dir + "entity2textlong_redirected.txt")
    save_and_append_results(no_class, work_dir + "no_class2.txt")
    save_and_append_results(no_long_text, work_dir + "no_long_text2.txt")
    print("done")


def query_disambiguration(triple_file, work_dir):
    no_class = []
    no_long_text = []
    ent2classes_l = []
    ent2longtext_l = []
    with open(triple_file) as f:
        all_triples = f.readlines()
    with open(work_dir + "no_class2.txt") as f:
        all_no_class_ents = f.readlines()
        for ent in tqdm(all_no_class_ents):
            ent = ent.strip()
            triples = list(filter(lambda x: ent in x.strip().split('\t'), all_triples))
            found = False
            for tri in triples:
                tri_hrt = tri.strip().split('\t')
                query_clause = f"<{tri_hrt[0]}> <{tri_hrt[1]}> <{tri_hrt[2]}>"
                query_clause = query_clause.replace(f"<{ent}>", "?x")
                query_str = f"SELECT distinct ?object " \
                    "FROM <http://dbpedia.org> WHERE {" \
                    f"<{ent}> <{DISAMBIGUATE}> ?x . " \
                    f"{query_clause} . " \
                    f"?x <{TYPE_OF}> ?object . " \
                    "} LIMIT 500"
                classes = get_query_values(query_str)
                if len(classes) == 0:
                    continue
                else:
                    ent2classes_l.append(f"{ent}\t" + ";".join(classes))
                    found = True
                    break
            if not found:
                no_class.append(ent)
    save_and_append_results(ent2classes_l, work_dir + "entity2type_disanbigurate.txt")

    with open(work_dir + "no_long_text2.txt") as f:
        all_no_longtext_ents = f.readlines()
        for ent in tqdm(all_no_longtext_ents):
            ent = ent.strip()
            triples = list(filter(lambda x: ent in x.split('\t'), all_triples))
            found = False
            for tri in triples:
                tri_hrt = tri.strip().split('\t')
                query_clause = f"<{tri_hrt[0]}> <{tri_hrt[1]}> <{tri_hrt[2]}>"
                query_clause = query_clause.replace(f"<{ent}>", "?x")
                query_str = f"SELECT distinct ?object " \
                    "FROM <http://dbpedia.org> WHERE {" \
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

    save_and_append_results(no_class, work_dir + "no_class3.txt")
    save_and_append_results(no_long_text, work_dir + "no_long_text3.txt")
    print("done")


def save_and_append_results(d_list, out_filename):
    out_file = Path(out_filename)
    if not out_file.parent.exists():
        out_file.parent.mkdir(exist_ok=False)

    with open(out_filename, encoding='utf-8', mode='a') as out_f:
        for item in d_list:
            out_f.write(item + '\n')
        out_f.close()


if __name__ == "__main__":
    # query_entity_text_and_class("../resources/DBpedia-politics/entity2id.txt", work_dir="../outputs/test_dbpedia/")
    # query_wiki_redirect("../outputs/test_dbpedia/")
    query_disambiguration("../resources/DBpedia-politics/PoliticalTriplesWD.txt", work_dir="../outputs/test_dbpedia/")