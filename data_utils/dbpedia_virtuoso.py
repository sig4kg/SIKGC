import re
from datetime import datetime
import platform
from SPARQLWrapper import SPARQLWrapper, JSON


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
    sparql.setTimeout(5)
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
