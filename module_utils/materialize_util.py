import numpy as np
from owlready2 import *
import pandas as pd
from abox_scanner.abox_utils import read_scanned_2_context_df, wait_until_file_is_saved, ContextResources
import scripts.run_scripts
from abox_scanner.abox_utils import ContextResources, read_hrt_2_df


def preparing_tbox_to_dllite(tbox_file, work_dir):
    # if dataset == 'dbpedia':
    #     tbox_2_nt_dbpedia(tbox_file, work_dir + "tbox.nt")
    # else:
    #     clean_nt(tbox_file, work_dir + "tbox.nt")
    if not os.path.exists(work_dir + "tbox_dllite.ttl"):
        scripts.run_scripts.to_dllite(tbox_file, work_dir)
        wait_until_file_is_saved(work_dir + "tbox_dllite.ttl")


# def merge_TBox_2_ABox(abox_file, tbox_file, work_dir):
#     df_a = pd.read_csv(abox_file, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ")
#     df_t = pd.read_csv(tbox_file, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ")
#     df = pd.concat([df_t, df_a])
#     df = df.drop_duplicates(keep='first')
#     df.to_csv(work_dir + "tbox_abox.nt", index=False, header=False, sep=' ')


def hrt_int_df_2_hrt_ntriples(context_resource: ContextResources, work_dir):
    df = context_resource.hrt_int_df.copy(deep=True)
    df[['head', 'tail']] = df[['head', 'tail']].applymap(lambda x: '<' + context_resource.id2ent[x] + '>')
    df[['rel']] = df[['rel']].applymap(lambda x: '<' + context_resource.id2rel[x] + '>')  # to int
    df['dot'] = '.'
    df[['head', 'rel', 'tail', 'dot']].to_csv(work_dir + "abox.nt", header=None, index=None, sep=' ')


def materialize(work_dir):
    # merge_TBox_2_ABox(work_dir + "abox.nt", work_dir + "tbox.nt", work_dir)
    scripts.run_scripts.run_materialization(work_dir)
    clean_nt(work_dir + "materialized_tbox_abox.nt", work_dir + "cleaned_tbox_abox.nt")
    wait_until_file_is_saved(work_dir + "cleaned_tbox_abox.nt")


def nt_2_hrt_int_df(in_file, context_resource: ContextResources):
    df = pd.read_csv(
        in_file, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ")
    df = df[['head', 'rel', 'tail']].apply(lambda x: x.str[1:-1])
    df[['head', 'tail']] = df[['head', 'tail']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df[['rel']] = df[['rel']].applymap(
        lambda x: context_resource.rel2id[x] if x in context_resource.rel2id else np.nan)  # to int
    df = df.dropna(how='any')
    return df


def tbox_2_nt_dbpedia(in_file: str, out_file):
    ont = get_ontology(in_file).load()
    # remove all annotation properties, cannot identify AnnotationProperty as TBOX is not complete.
    default_world.sparql('''DELETE {?s ?p ?o . } 
                            WHERE {?s ?p ?o .
                            Filter (?p in (<http://www.w3.org/2000/01/rdf-schema#label>, 
                            <http://www.w3.org/2002/07/owl#versionInfo>,
                            <http://purl.org/dc/terms/issued>,
                            <http://purl.org/dc/terms/description>,
                            <http://purl.org/dc/terms/modified>,
                            <http://purl.org/dc/terms/title>,
                            <http://purl.org/vocab/vann/preferredNamespaceUri>,   
                            <http://purl.org/vocab/vann/preferredNamespacePrefix>,
                            <http://purl.org/dc/terms/publisher>,
                            <http://www.w3.org/2000/01/rdf-schema#comment>))}''')
    # out_file_name = in_file[in_file.rindex('/')+1:in_file.rindex('.')]
    ont.save(out_file, "ntriples")


ANNOTATION_REL = ['<http://www.w3.org/2000/01/rdf-schema#label>',
                  '<http://www.w3.org/2002/07/owl#versionInfo>',
                  '<http://purl.org/dc/terms/issued>',
                  '<http://purl.org/dc/terms/description>',
                  '<http://purl.org/dc/terms/modified>',
                  '<http://purl.org/dc/terms/title>',
                  '<http://purl.org/vocab/vann/preferredNamespaceUri>',
                  '<http://purl.org/vocab/vann/preferredNamespacePrefix>',
                  '<http://purl.org/dc/terms/publisher>',
                  '<http://ste-lod-crew.fr/nell/ontology/humanformat> ',
                  '<http://ste-lod-crew.fr/nell/ontology/instancetype>',
                  '<http://www.w3.org/2000/01/rdf-schema#comment>',
                  '^^<http://www.w3.org/2001/XMLSchema#boolean>']


def clean_nt(in_nt_file: str, out_file):
    with open(in_nt_file) as f:
        with open(out_file, encoding='utf-8', mode='w') as out_f:
            lines = f.readlines()
            for l in lines:
                if not l.startswith('<'):
                    continue
                if any([x in l for x in ANNOTATION_REL]):
                    continue
                out_f.write(l)
        out_f.close()
    f.close()


# do not work on NELL.ontology.ttl
# def owl_2_nt(in_file, work_dir):
#     ont = get_ontology(in_file).load()
#     out_file_name = in_file[in_file.rindex('/') + 1:in_file.rindex('.')]
#     # owlready2 save do not parse well for large files. it use _:num instead of individual uri.
#     # ont.save(work_dir+out_file_name+".nt", "ntriples")
#     triples = ont.get_triples()
#     extended_triple_tuples = [(ont._unabbreviate(x[0]),
#                                ont._unabbreviate(x[1]),
#                                ont._unabbreviate(x[2]))
#                               for x in ont.get_triples() if isinstance(x[2], int)
#                               and x[0] >= 0
#                               and x[1] >= 0
#                               and x[2] >= 0]
#     df = pd.DataFrame(data=extended_triple_tuples)
#     df = df.apply(lambda x: '<' + x + '>')
#     df['dot'] = '.'
#     df.to_csv(work_dir + out_file_name + ".nt", header=None, index=None, sep=' ')


if __name__ == "__main__":
    # hrt_2_nt("../resources/DBpedia-politics/PoliticalTriplesWD.txt", "../outputs/m/")
    # remove_TBox_from_ABox("../outputs/cm/")
    # owl_2_nt("../outputs/cm/materialized_tbox_abox.owl", "../outputs/cm/")
    # materialize("../outputs/cm/")
    clean_nt("../resources/NELL/NELL.ontology.nt", "../resources/NELL/NELL-ontology-clean.nt")