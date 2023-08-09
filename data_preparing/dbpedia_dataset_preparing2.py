import dbpedia_dataset_preparing


def get_types(triple_file, work_dir):
    all_triples, entities, rels = dbpedia_dataset_preparing.read_triples_entities_rels_nt(triple_file, ' ')
    dbpedia_dataset_preparing.generate_entity2type(all_triples, entities, work_dir)
    dbpedia_dataset_preparing.query_entity_text(entities, work_dir)
    dbpedia_dataset_preparing.query_rel_text(rels, work_dir)


if __name__ == "__main__":
    get_types("../resources/DB15K/DB15K_EntityTriples.txt", "../outputs/db15k/")