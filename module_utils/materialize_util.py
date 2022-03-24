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


def learn_type_assertions_konclude(work_dir):
    # cmd = ['java',
    #        f'-DkoncludeBinary={koncludeBinary}'
    #        '-Dtask=Materialize',
    #        '-Dschema=tbox_abox.nt',
    #        '-Doutput_dir=./',
    #        '-jar',
    #        f'{work_dir}TBoxTREAT-1.0.jar']
    koncludeBinary = osp.join(os.getcwd(), "../java_owlapi/Konclude/Binaries/Konclude")
    cmd = f"java -DkoncludeBinary={koncludeBinary} -Dtask=Konclude -Dschema=tbox_abox.nt -Doutput_dir=./ -jar {work_dir}TBoxTREAT-1.0.jar"
    os.system(cmd)
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)
    # for line in iter(p.stdout.readline, b''):
    #     print(line)
    #     if subprocess.Popen.poll(p) is not None and line == b'':
    #         break
    # p.stdout.close()
    returncode = wait_until_file_is_saved(work_dir + "materialized_tbox_abox.nt")
    return returncode


def materialisation_trowl(work_dir):
    cmd = f"java -Dtask=TrOWL -Dschema=tbox_abox.nt -Doutput_dir=./ -jar {work_dir}TBoxTREAT-1.0.jar"
    os.system(cmd)
    returncode = wait_until_file_is_saved(work_dir + "materialized_tbox_abox.nt")
    return returncode


def materialize(work_dir, context_resource: ContextResources, abox_scanner: AboxScannerScheduler):
    os.system('../scripts/prepare_materialize.sh ' + work_dir[:-1])
    # learn type assertions
    new_ent2types = {}
    new_property_assertions = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
    start_time = datetime.datetime.now()
    has_output = materialisation_trowl(work_dir)
    if has_output:
        print(f"The type assertion reasoning duration is {datetime.datetime.now() - start_time}")
        new_ent2types, new_property_assertions = split_materialisation_result(work_dir + "materialized_tbox_abox.nt", context_resource)
    # learn property assertions
    # new_property_assertions = abox_scanner.scan_generator_patterns()
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
    context_resource.type_count += new_count
    return new_count


# we only keep type assertions
def split_materialisation_result(in_file, context_resource: ContextResources):
    df = pd.read_csv(
        in_file, header=None, names=['head', 'rel', 'tail'], sep=" ", usecols=range(3)).drop_duplicates(
        keep='first').reset_index(drop=True)
    df_types = df.query("rel==@RDFTYPE1")
    df_properties = pd.concat([df, df_types]).drop_duplicates(
        keep=False)
    # get type dict
    df_types = df_types[['head', 'tail']].apply(lambda x: x.str[1:-1])
    df_types['head'] = df_types[['head']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df_types['tail'] = df_types[['tail']].applymap(
        lambda x: context_resource.class2id[x] if x in context_resource.class2id else np.nan)  # to int
    df_types = df_types.dropna(how='any').astype('int64')
    groups = df_types.groupby('head')
    new_ent2types = dict()
    for g in groups:
        ent = g[0]
        types = g[1]['tail'].tolist()
        new_ent2types.update({ent: types})
    # get property assertions in hrt_int_df
    df_properties = df_properties.apply(lambda x: x.str[1:-1])
    df_properties[['head', 'tail']] = df_properties[['head', 'tail']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df_properties['rel'] = df_properties['rel'].apply(
        lambda x: context_resource.op2id[x] if x in context_resource.op2id else np.nan)  # to int
    df_properties = df_properties.dropna(how='any').astype('int64')
    return new_ent2types, df_properties


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


if __name__ == "__main__":
    dft = pd.read_csv("../resources/materialized_tbox_abox.nt", header=None,
                      names=['head', 'rel', 'tail', 'dot'], sep=" ").drop_duplicates(
        keep='first').reset_index(drop=True)
    dft = dft.query("rel==@RDFTYPE1")
