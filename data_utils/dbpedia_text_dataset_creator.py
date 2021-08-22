from data_utils.dbpedia_virtuoso import *
from pathlib import Path
import platform
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm


DEFAULT_GRAPH = "http://dbpedia.org"
PREFIX_DBO = "http://dbpedia.org/ontology/"
PREFIX_SCHEMA = "http://www.w3.org/2001/XMLSchema"
PREFIX_SUBCLASSOF = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
PREFIX_DBR = "http://dbpedia.org/resource/"
PREFIX_TYPE_OF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
PREFIX_TYPE = 'http://purl.org/dc/terms/subject'
RECORD_LIMIT = 200
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
        f"<{resource_uri}> <{PREFIX_TYPE_OF}> ?object . " \
        "} LIMIT 500"
    all_classes = get_query_values(query_str)
    return all_classes


def get_long_text(resource_uri):
    query_str = f"SELECT distinct ?object " \
        "FROM <http://dbpedia.org> WHERE {" \
        f"<{resource_uri}> <http://www.w3.org/2000/01/rdf-schema#comment> ?object . " \
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


def save_and_append_results(d_list, out_filename):
    out_file = Path(out_filename)
    if not out_file.parent.exists():
        out_file.parent.mkdir(exist_ok=False)

    with open(out_filename, encoding='utf-8', mode='a') as out_f:
        for item in d_list:
            out_f.write(item + '\n')
        out_f.close()


if __name__ == "__main__":
    query_entity_text_and_class("../resources/DBpedia-politics/entity2id.txt", work_dir="../outputs/test/")

