import dbpedia_dataset_preparing
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import pickle
from tqdm import tqdm
import numpy as np
import bz2


DBPEDIA_GRAPH_URL = LOCALHOST = "https://dbpedia.org/sparql"


def format_nt(triple_nt_file, work_dir):
    all_triples, _, _ = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_nt_file, ' ')
    with open(work_dir + "abox_hrt_uri.txt", 'w') as f:
        for item in all_triples:
            f.write(f"{item[0]}\t{item[1]}\t{item[2]}\n")
        print(work_dir + "abox_hrt_uri.txt" + " has been saved.")


def get_types(triple_file, work_dir):
    all_triples, entities, rels = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_file, ' ')
    dbpedia_dataset_preparing.generate_entity2type(all_triples, entities, work_dir)
    # dbpedia_dataset_preparing.query_entity_text(entities, work_dir)
    # dbpedia_dataset_preparing.query_rel_text(rels, work_dir)


# def get_ent_dict_and_save(triple_file, separator=' '):
#     _, entities, _ = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_file, separator)
#     dbpedia2wikiid = dict()
#     for ent in tqdm(entities):
#         wiki_ids = query_ent_wikiid(ent)
#         if len(wiki_ids) > 0:
#             dbpedia2wikiid.update({ent: wiki_ids})
#     with open('../resources/DB15K/ent2wikiid.pkl', 'wb') as f:
#         pickle.dump(dbpedia2wikiid, f)


def get_ent_dict_and_save2(triple_file, out_file, separator=' '):
    _, entities, _ = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_file, separator)
    dbpedia2wikiid = dict()
    wikistr = "wikidata"
    with bz2.BZ2File('/Users/sylvia.wang/Downloads/sameAs_lang=en.ttl.bz2', 'r') as source_file:
        for line_b in tqdm(source_file, mininterval=5, total=127331197):
            line = line_b.decode("utf-8")
            if wikistr not in line:
                continue
            items = line.split(' ')
            ent = items[0][1:-1]
            if ent in entities:
                wikiid = items[2][1:-1].split('/')[-1]
                dbpedia2wikiid.update({ent: wikiid})
    with open(out_file, 'wb') as f:
        pickle.dump(dbpedia2wikiid, f)


def get_rel_dict_and_save(triple_file, out_file, separator=' '):
    _, _, rels = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_file, separator)
    dbpedia_rel2wikiid = dict()
    for rel in tqdm(rels):
        wiki_ids = query_rel_wikiid(rel)
        if len(wiki_ids) > 0:
            dbpedia_rel2wikiid.update({rel: wiki_ids})
    with open(out_file, 'wb') as f:
        pickle.dump(dbpedia_rel2wikiid, f)


def get_all_classes_relations(entity2class_uri_file, hrt_uri_file, out_dir):
    df = pd.read_csv(hrt_uri_file, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ", error_bad_lines=False, engine="python")
    df[['rel']].drop_duplicates(keep="first").applymap(lambda x: x[1:-1]).to_csv(out_dir + "properties.txt", header=False, index=False, mode='w')
    all_types = []
    with open(entity2class_uri_file) as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split('\t')
            classes = items[1].split(';')
            all_types.extend(classes)
    all_types = list(set(all_types))
    dbpedia_dataset_preparing.save_and_append_results(all_types, out_dir + "types.txt")


def get_negations(neg_file, work_dir):
    # read negations
    negs1 = pd.read_csv(neg_file, header=None,
                       names=['sid', 'slabel', 'pid', 'plabel', 'oid', 'olabel', 'score', 'exp'],
                       sep="\t")
    negs2 = negs1[['sid', 'pid', 'oid']]
    del negs1
    # load entityid map and relid map to DBpedia
    with open('../resources/DB15K/rel2wikiid.pkl', 'rb') as f:
        dbpedia2wiki_rel = pickle.load(f)
    with open('../resources/DB15K/ent2wikiid.pkl', 'rb') as f:
        dbpedia2wiki_ent = pickle.load(f)
    # generete wiki2dbpedia dict
    wiki2dbpedia_ent = dict()
    wiki2dbpedia_rel = dict()
    for key, value in dbpedia2wiki_rel.items():
        for wikiid in value:
            wiki2dbpedia_rel.update({wikiid: key})
    for key, value in dbpedia2wiki_ent.items():
        for wikiid in value:
            wiki2dbpedia_ent.update({wikiid: key})

    # filter entites and rels in wikineg
    negs2[['sid', 'oid']] = negs2[['sid', 'oid']].applymap(lambda x:  wiki2dbpedia_ent[x] if x in wiki2dbpedia_ent else np.nan)
    negs2[['pid']] = negs2[['pid']].applymap(lambda x:  wiki2dbpedia_rel[x] if x in wiki2dbpedia_rel else np.nan)  # to uri
    negs2 = negs2.dropna(how='any')
    negs2.to_csv(work_dir + "negs.csv", header=False, index=False, mode='w')


def query_rel_wikiid(resource_uri):
    equivalent = "<http://www.w3.org/2002/07/owl#equivalentProperty>"
    query_str = f'SELECT distinct ?o ' \
                'WHERE {' \
                f'<{resource_uri}> {equivalent} ?o . ' \
                '} LIMIT 500'
    sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL)
    sparql.setTimeout(20)
    sparql.setQuery(query_str)
    sparql.setReturnFormat(JSON)
    values = []
    try:
        response = sparql.query()
        results = response.convert()
        for record in results["results"]["bindings"]:
            wikiid = record['o']['value']
            if 'wikidata' not in wikiid:
                continue
            values.append(wikiid.split('/')[-1])
        response.response.close()
        return values
    except Exception as err:
        print("failed to query dbpedia virtuoso...")
        return values



def query_ent_wikiid(resource_uri):
    same_as = "<http://www.w3.org/2002/07/owl#sameAs>"
    query_str = f'SELECT distinct ?o ' \
                'WHERE {' \
                f'<{resource_uri}> {same_as} ?o . ' \
            'filter contains(str(?o), "wikidata")' \
                '} LIMIT 500'
    sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL)
    sparql.setTimeout(20)
    sparql.setQuery(query_str)
    sparql.setReturnFormat(JSON)
    values = []
    try:
        response = sparql.query()
        results = response.convert()
        for record in results["results"]["bindings"]:
            wikiid = record['o']['value']
            values.append(wikiid.split('/')[-1])
        response.response.close()
        return values
    except Exception as err:
        print("failed to query dbpedia virtuoso...")
        return values


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
