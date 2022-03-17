import numpy as np
from owlready2 import *
import pandas as pd
import os.path as osp
from abox_scanner.abox_utils import wait_until_file_is_saved
from subprocess import Popen, PIPE, STDOUT
from abox_scanner.ContextResources import ContextResources
import subprocess
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler

RDFTYPE1 = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
RDFTYPE2 = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def learn_type_assertions(work_dir, koncludeBinary="../java_owlapi/Konclude/Binaries/Konclude"):
    # cmd = ['java',
    #        f'-DkoncludeBinary={koncludeBinary}'
    #        '-Dtask=Materialize',
    #        '-Dschema=tbox_abox.nt',
    #        '-Doutput_dir=./',
    #        '-jar',
    #        f'{work_dir}TBoxTREAT-1.0.jar']
    koncludeBinary = osp.join(os.getcwd(), "../java_owlapi/Konclude/Binaries/Konclude")
    cmd = f"java -DkoncludeBinary={koncludeBinary} -Dtask=Materialize -Dschema=tbox_abox.nt -Doutput_dir=./ -jar {work_dir}TBoxTREAT-1.0.jar"
    returncode = os.system(cmd)
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)
    # for line in iter(p.stdout.readline, b''):
    #     print(line)
    #     if subprocess.Popen.poll(p) is not None and line == b'':
    #         break
    # p.stdout.close()
    wait_until_file_is_saved(work_dir + "materialized_tbox_abox.nt")
    return returncode


def materialize(work_dir, context_resource: ContextResources, abox_scanner: AboxScannerScheduler):
    os.system('../scripts/prepare_materialize.sh ' + work_dir[:-1])
    # learn type assertions
    new_ent2types = {}
    p = learn_type_assertions(work_dir)
    if p == 0:
        new_ent2types = type_nt_2_entity2type(work_dir + "materialized_tbox_abox.nt", context_resource)
    # learn property assertions
    new_property_assertions = abox_scanner.scan_generator_patterns()
    return new_ent2types, new_property_assertions


# return new count
def update_ent2class(context_resource: ContextResources, new_ent2types) -> int:
    old_ent2types = context_resource.entid2classids
    new_count = 0
    for ent in new_ent2types:
        if ent in old_ent2types:
            old_types = set(old_ent2types[ent])
            new_types = set(new_ent2types[ent])
            diff = new_types.difference(old_types)
            if len(diff) > 0:
                new_count = new_count + len(diff)
                old_ent2types[ent].extend(list(diff))
    return new_count


# we only keep type assertions
def type_nt_2_entity2type(in_file, context_resource: ContextResources):
    df = pd.read_csv(
        in_file, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ").drop_duplicates(
        keep='first').reset_index(drop=True)
    df = df.query("rel==@RDFTYPE1")
    df = df[['head', 'tail']].apply(lambda x: x.str[1:-1])
    df['head'] = df[['head']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df['tail'] = df[['tail']].applymap(
        lambda x: context_resource.class2id[x] if x in context_resource.class2id else np.nan)  # to int
    df = df.dropna(how='any').astype('int64')
    groups = df.groupby('head')
    new_ent2types = dict()
    for g in groups:
        ent = g[0]
        types = g[1]['tail'].tolist()
        new_ent2types.update({ent: types})
    return new_ent2types


# def tbox_2_nt_dbpedia(in_file: str, out_file):
#     ont = get_ontology(in_file).load()
#     # remove all annotation properties, cannot identify AnnotationProperty as TBOX is not complete.
#     default_world.sparql('''DELETE {?s ?p ?o . }
#                             WHERE {?s ?p ?o .
#                             Filter (?p in (<http://www.w3.org/2000/01/rdf-schema#label>,
#                             <http://www.w3.org/2002/07/owl#versionInfo>,
#                             <http://purl.org/dc/terms/issued>,
#                             <http://purl.org/dc/terms/description>,
#                             <http://purl.org/dc/terms/modified>,
#                             <http://purl.org/dc/terms/title>,
#                             <http://purl.org/vocab/vann/preferredNamespaceUri>,
#                             <http://purl.org/vocab/vann/preferredNamespacePrefix>,
#                             <http://purl.org/dc/terms/publisher>,
#                             <http://www.w3.org/2000/01/rdf-schema#comment>))}''')
#     # out_file_name = in_file[in_file.rindex('/')+1:in_file.rindex('.')]
#     ont.save(out_file, "ntriples")


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


# if __name__ == "__main__":
#     tbox_2_nt_dbpedia("../resources/DBpediaP/dbpedia_2016-10.owl", "../resources/DBpedia-politics/less_dbpedia_tbox.nt")