from datasets import list_datasets, load_dataset, list_metrics, load_metric
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def load_nell_sentense(output_dir):
    # Load a dataset and print the first example in the training set
    nell_dataset = load_dataset('nell', 'nell_belief_sentences')
    # with open(output_dir + 'nell_sentences.csv', 'w') as f:
    #     for line in nell_dataset['train'][0:10]:
    #         f.write(line + "\n")
    df = pd.DataFrame(nell_dataset['train'][:])
    df.to_csv(output_dir + 'nell_sentences.csv', sep='\t')



def nell_ent_to_sentenses(data_file, output_dir):
    df = pd.read_csv(
        data_file, sep="\t")
    df.pop('Unnamed: 0')
    # only_select_one_sentence_per_tri = df.loc[df.reset_index().groupby(['entity', 'relation', 'value'])['count'].idxmax()]
    tri_sort = df.groupby(['entity', 'relation', 'value'], group_keys=False).apply(
        lambda x: x.sort_values(['count'], ascending=False))
    tri_sort.reset_index(drop=True)
    tri_sents = tri_sort.groupby(['entity', 'relation', 'value', 'score'], group_keys=False, as_index=False).agg(list)
    filtered = tri_sents[['entity', 'relation', 'value', 'score', 'sentence']]
    entity_sents = filtered.groupby(["entity"])
    out_file1 = Path(output_dir + "entity2textlong_all.txt")
    if not out_file1.parent.exists():
        out_file1.parent.mkdir(exist_ok=False)
    with open(out_file1, 'w') as f:
        for entity, group in tqdm(entity_sents):
            tris_s = group['sentence']
            first_s_per_tri = []
            for s_l in tris_s:
                for s in s_l:
                    if s.count(' ') <= 64:
                        first_s_per_tri.append(s.replace("\"", ''))
                        break
            entity_sents = '. '.join(first_s_per_tri)
            entity_sents = entity_sents.replace('..', '.').replace('[[ ', '').replace(' ]]', '')
            f.write(f"{entity.replace(':', '_')}\t{entity_sents}\n")
    filtered['entity'] = filtered['entity'].apply(lambda x: x.replace(":", "_"))
    filtered.to_csv(output_dir + "tri-sents.csv", header=None, index=None, sep='\t', mode='a')


def nell_ent_to_description(data_files, output_dir):
    entities = []
    all_entities = pd.DataFrame(columns=['entity', 'text'])
    for in_file in tqdm(data_files):
        with open(in_file) as f:
            lines = f.readlines()
            for l in lines:
                items = l.split('\t')
                entity = items[0].strip()
                entity_str = items[-5].strip()
                value = items[2].strip()
                value_str = items[-4].strip()
                if entity_str != '':
                    entities.append([entity, entity_str])
                if value_str != '':
                    entities.append([value, value_str])
            tmp_df = pd.DataFrame(data=entities, columns=['entity', 'text'])
            all_entities = pd.merge(all_entities, tmp_df, how='outer').drop_duplicates(keep='first').dropna(axis=0,
                                                                                                          how='any')
    ent2Category = dict()
    ent2literal = dict()
    # ent_g = all_entities.groupby(['entity'], group_keys=False, as_index=False).agg(list)
    # rel_view = keep_info[['Relation']].drop_duplicates(keep=False)
    for idx, row in tqdm(all_entities.iterrows()):
        entity = row['entity'].replace('concept:', '').replace(':', '_')
        concept = row['entity'].split(':')[1] if ':' in row['entity'] else ''
        ent_str = row['text'] if not pd.isna(row['text']) else entity.split('_')[-1]
        if entity != '' and entity_str != '':
            ent2literal.update({entity: ent_str})
        if concept != '':
            ent2Category.update({entity: concept})

    out_file1 = Path(output_dir + "entity2text_all.txt")
    out_file2 = Path(output_dir + "entity2type_all.txt")
    if not out_file1.parent.exists():
        out_file1.parent.mkdir(exist_ok=False)
    with open(out_file1, 'w') as f:
        for key in ent2literal:
            f.write(f"{key}\t{ent2literal[key]}\n")
    with open(out_file2, 'w') as f2:
        for key in ent2Category:
            f2.write(f"{key}\t{ent2Category[key]}\n")


def read_file_to_dict(filename):
    result = dict()
    with open(filename) as f:
        lines = f.readlines()
        for l in lines:
            items = l.split('\t')
            if len(items) != 2:
                print(l)
            key = items[0].strip()
            value = items[1].strip()
            result.update({key: value})
    return result


def nell_tidyup_text_files(work_dir):
    nell_tris = pd.read_csv(work_dir + 'NELLKG0.txt', header=None, names=['head', 'relation', 'tail'], sep='\t', error_bad_lines=False, engine="python")
    all_entities = pd.merge(nell_tris[['head']].rename(columns={'head': 'entity'}),
                            nell_tris[['tail']].rename(columns={'tail': 'entity'}), how='outer').drop_duplicates(
        keep='first')
    all_relations = nell_tris[['relation']].drop_duplicates(keep='first')
    entity2text = read_file_to_dict(work_dir + 'entity2text_all.txt')
    entity2textlong = read_file_to_dict(work_dir + 'entity2textlong_all.txt')
    rel2text = read_file_to_dict(work_dir + 'relation2text_all.txt')

    count_hit = 0
    count_nohit = 0
    for _, ent in all_entities.iterrows():
        if ent['entity'] not in entity2textlong:
            count_nohit += 1
        else:
            count_hit += 1
    print(f"count hit: {count_hit}")
    print(f"count no hit: {count_nohit}")

    ent_text_df = all_entities[['entity']]
    ent_text_df['text'] = ent_text_df.apply(lambda row: entity2text[row.entity] if row.entity in entity2text else row.entity.split('_', 1)[-1].replace('_', ' '), axis=1)
    ent_text_df.to_csv(work_dir + "entity2text.txt", header=None, index=None, sep='\t', mode='a')
    ent_type_df = all_entities[['entity']]
    ent_type_df['type'] = ent_type_df.apply(lambda row: row.entity.split('_', 1)[0], axis=1)
    ent_type_df.to_csv(work_dir + "entity2type.txt", header=None, index=None, sep='\t', mode='a')
    ent_textlong_df = all_entities[['entity']]
    ent_textlong_df['text'] = ent_textlong_df.apply(lambda row: entity2textlong[row.entity] if row.entity in entity2textlong else row.entity.split('_', 1)[-1].replace('_', ' '), axis=1)
    ent_textlong_df.to_csv(work_dir + "entity2textlong.txt", header=None, index=None, sep='\t', mode='a')
    rel_text_df = all_relations[['relation']]
    rel_text_df['text'] = rel_text_df.apply(lambda row: rel2text[row.relation] if row.relation in rel2text else row.relation, axis=1)
    rel_text_df.to_csv(work_dir + "relation2text.txt", header=None, index=None, sep='\t', mode='a')


def filter_small_data(in_dir, out_dir):
    nell_tris = pd.read_csv(in_dir + 'NELLKG0.txt', header=None, names=['head', 'relation', 'tail'], sep='\t',
                            error_bad_lines=False, engine="python")
    entity2textlong = read_file_to_dict(in_dir + 'entity2textlong_all.txt')
    del_rows = nell_tris[nell_tris['head'] not in entity2textlong or nell_tris['tail'] not in entity2textlong].index
    filtered_nell = nell_tris.drop(del_rows, axis=0)
    entity2text = read_file_to_dict(in_dir + 'entity2text.txt')
    rel2text = read_file_to_dict(in_dir + 'relation2text.txt')

    all_entities = pd.merge(filtered_nell[['head']].rename(columns={'head': 'entity'}),
                            filtered_nell[['tail']].rename(columns={'tail': 'entity'}), how='outer').drop_duplicates(
        keep='first')
    ent_text_df = all_entities[['entity']]
    ent_text_df['text'] = ent_text_df.apply(
        lambda row: entity2text[row.entity] if row.entity in entity2text else row.entity.split('_', 1)[-1].replace('_',
                                                                                                                   ' '),
        axis=1)
    ent_text_df.to_csv(out_dir + "entity2text.txt", header=None, index=None, sep='\t', mode='a')
    ent_type_df = all_entities[['entity']]
    ent_type_df['type'] = ent_type_df.apply(lambda row: row.entity.split('_', 1)[0], axis=1)
    ent_type_df.to_csv(out_dir + "entity2type.txt", header=None, index=None, sep='\t', mode='a')
    ent_textlong_df = all_entities[['entity']]
    ent_textlong_df['text'] = ent_textlong_df.apply(
        lambda row: entity2textlong[row.entity] if row.entity in entity2textlong else row.entity.split('_', 1)[
            -1].replace('_', ' '), axis=1)
    ent_textlong_df.to_csv(out_dir + "entity2textlong.txt", header=None, index=None, sep='\t', mode='a')

    all_relations = filtered_nell[['relation']].drop_duplicates(keep='first')
    rel_text_df = all_relations[['relation']]
    rel_text_df['text'] = rel_text_df.apply(
        lambda row: rel2text[row.relation] if row.relation in rel2text else row.relation, axis=1)
    rel_text_df.to_csv(out_dir + "relation2text.txt", header=None, index=None, sep='\t', mode='a')


NELLONTO = "http://ste-lod-crew.fr/nell/ontology/"
NELLRES = "http://ste-lod-crew.fr/nell/resource/"


def format_NELL(abox_file, out_file):
    df = pd.read_csv(abox_file, header=None, names=['head', 'rel', 'tail'], sep="\t", error_bad_lines=False, engine="python")
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: f'{NELLRES}{x}')
    df[['rel']] = df[['rel']].applymap(lambda x: f'{NELLONTO}{x}')
    df.to_csv(out_file, index=False, header=False, sep='\t', mode='w')


def format_NELL_entity2type(abox_file, out_file):
    nell_tris = pd.read_csv(abox_file, header=None, names=['head', 'relation', 'tail'], sep='\t',
                            error_bad_lines=False, engine="python")
    all_entities = pd.concat([nell_tris['head'], nell_tris['tail']], ignore_index=True).drop_duplicates(keep='first')
    all_entities = pd.DataFrame(all_entities, columns=['entity'])
    all_entities['type'] = all_entities['entity'].apply(lambda x: NELLONTO + x.split('_', 1)[0])
    all_entities[['entity']] = all_entities[['entity']].applymap(lambda x: NELLRES + x)
    all_entities.to_csv(out_file, header=False, index=False, sep='\t', mode='w')


if __name__ == "__main__":
    format_NELL("../resources/NELL/abox_hrt.txt", "../resources/NELL/abox_hrt_uri.txt")
    # format_NELL_entity2type("../resources/NELL/NELLKG0.txt", "../resources/NELL-patterns/entity2type.txt")
# nell_ent_to_sentenses("../resources/NELL-995_2/nell_sentences.csv", output_dir="../resources/NELL-995_2/")
# nell_ent_to_description([
#     "../resources/NELL-995_2/nell115.csvaa",
#     "../resources/NELL-995_2/nell115.csvab",
#     "../resources/NELL-995_2/nell115.csvac",
#     "../resources/NELL-995_2/nell115.csvad"],
#     output_dir='../outputs/test_nell/')
# nell_tidyup_text_files('../resources/NELL-995_2/')
# read_file_to_dict('../resources/NELL-995_2/relation2text_all.txt')
# filter_small_data("../resources/NELL-995_2/", "../resources/NELL-995-small/")