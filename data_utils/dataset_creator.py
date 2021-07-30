from datasets import list_datasets, load_dataset, list_metrics, load_metric
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def load_nell_sentense(output_dir):
    # Load a dataset and print the first example in the training set
    nell_dataset = load_dataset('nell', 'nell_belief_sentences')
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
            first_s_per_tri = [s_l[0] for s_l in tris_s]
            entity_sents = '. '.join(first_s_per_tri)
            entity_sents = entity_sents.replace('..', '.').replace('[[ ', '').replace(' ]]', '')
            f.write(f"{entity.replace(':', '_')}\t{entity_sents}\n")
    filtered['entity'] = filtered['entity'].apply(lambda x: x.replace(":", "_"))
    filtered.to_csv(output_dir + "tri-sents.csv", header=None, index=None, sep='\t', mode='a')


def nell_ent_to_description(data_file, output_dir):
    df = pd.read_csv(
        data_file, sep="\t")
    ent2Category = dict()
    ent2literal = dict()
    keep_info = df[['Entity', 'Relation', 'Value', 'Best Entity literalString', 'Best Value literalString']]
    entities_view = keep_info[['Entity', 'Best Entity literalString']].\
        rename(columns={'Entity': 'entity', 'Best Entity literalString': 'text'})
    values_view = keep_info[['Value', 'Best Value literalString']].\
        rename(columns={'Value': 'entity', 'Best Value literalString': 'text'})
    all_entities = pd.merge(entities_view, values_view, how='outer').drop_duplicates(keep=False)
    ent_g = all_entities.groupby(['entity'], group_keys=False, as_index=False).agg(list)
    # rel_view = keep_info[['Relation']].drop_duplicates(keep=False)

    for idx, row in tqdm(ent_g.iterrows()):
        entity = row['entity'].replace('concept:', '').replace(':', '_')
        concept = row['entity'].split(':')[1] if ':' in row['entity'] else ''
        ent_str = row['text'][0] if not pd.isna(row['text']) else entity.split('_')[-1]
        if entity != '':
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


def nell_tidyup_text_files(work_dir):
    nell_tris = pd.read_csv(work_dir + 'NELLKG0.txt', header=None, names=['head', 'relation', 'tail'], sep='\t')
    all_entities = pd.merge(nell_tris[['head']].rename(columns={'head': 'entity'}), nell_tris[['tail']].rename(columns={'tail': 'entity'}), how='outer').drop_duplicates(keep=False)
    all_relations = nell_tris[['relation']].drop_duplicates(keep=False)
    entity_text = pd.read_csv(work_dir + 'entity2text_all.txt', header=None, names=['entity', 'text'], sep='\t')
    entity_type = pd.read_csv(work_dir + 'entity2type_all.txt', header=None, names=['entity', 'type'], sep='\t')
    rel_text = pd.read_csv(work_dir + 'relation2text_all.txt', header=None, names=['relation', 'text'], sep='\t')
    entity_longtext = pd.read_csv(work_dir + 'entity2textlong_all.txt', header=None, names=['entity', 'text'], sep='\t')
    entity2text = {row['entity']: row['text'] for _, row in entity_text.iterrows()}
    entity2type = {row['entity']: row['type'] for _, row in entity_type.iterrows()}
    entity2textlong = {row['entity']: row['text'] for _, row in entity_longtext.iterrows()}
    rel2text = {row['relation']: row['text'] for _, row in rel_text.iterrows()}
    ent_text_df = all_entities[['entity']]
    ent_text_df['text'] = ent_text_df.apply(lambda row: entity2text[row.entity], axis=1)
    ent_text_df.to_csv(work_dir + "entity2text.txt", header=None, index=None, sep='\t', mode='a')
    ent_type_df = all_entities[['entity']]
    ent_type_df['type'] = ent_type_df.apply(lambda row: entity2type[row.entity], axis=1)
    ent_type_df.to_csv(work_dir + "entity2type.txt", header=None, index=None, sep='\t', mode='a')
    ent_textlong_df = all_entities[['entity']]
    ent_textlong_df['text'] = ent_textlong_df.apply(lambda row: entity2textlong[row.entity], axis=1)
    ent_textlong_df.to_csv(work_dir + "entity2textlong.txt", header=None, index=None, sep='\t', mode='a')
    rel_text_df = all_relations[['relation']]
    rel_text_df['text'] = rel_text_df.apply(lambda row: rel2text[row.relation], axis=1)
    rel_text_df.to_csv(work_dir + "relation2text.txt", header=None, index=None, sep='\t', mode='a')


# load_nell_sentense()
# nell_ent_to_sentenses("../resources/NELL-995_2/nell_sentences.csv", output_dir="../outputs/test_nell/")
nell_ent_to_description("../resources/NELL-995_2/NELL.08m.1115.esv.csv", output_dir='../outputs/test_nell/')
# nell_ent_to_sentenses("../resources/nell100.csv", output_dir="../outputs/test/")
# nell_tidyup_text_files('../resources/NELL-995_2/')
