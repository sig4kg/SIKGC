import numpy as np
import pandas as pd
import os.path as osp
from abox_scanner.abox_utils import wait_until_file_is_saved
from abox_scanner.ContextResources import ContextResources
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import os
import datetime


RDFTYPE1 = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
RDFTYPE2 = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class MaterialisationReasoner(ABC):
    @abstractmethod
    def do_materialise(self, *args):
        pass

    @abstractmethod
    def parse_result(self, *args):
        pass

class MaterialisationKonclude(MaterialisationReasoner):
    def __init__(self, work_dir, context_resource: ContextResources, exclude_rels=[]):
        self.context_resource = context_resource
        self.work_dir = work_dir
        self.exclude_rels = exclude_rels

    def do_materialise(self):
        if not os.path.exists(self.work_dir + "role_queries.sparql"):
            prepare_konclude_relation_queries(self.work_dir, self.exclude_rels)

        koncludeBinary = osp.join(os.getcwd(), "../java_owlapi/Konclude/Binaries/Konclude")
        # get type assertions and relation assertions
        cmd = f"java -DkoncludeBinary={koncludeBinary} -Dtask=Konclude -Dschema=tbox_abox.nt -Dsparqls=role_queries.sparql -Doutput_dir=./  -jar {self.work_dir}TBoxTREAT-1.0.jar"
        os.system(cmd)
        wait_until_file_is_saved(self.work_dir + "materialized_role_instance.xml", 60*3)
        wait_until_file_is_saved(self.work_dir + "materialized_tbox_abox.nt", 60 * 3)
        return self.parse_result()

    def parse_result(self):
        new_ent2types = {}
        df_properties = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if os.path.exists(self.work_dir + "materialized_tbox_abox.nt"):
            df = pd.read_csv(
                self.work_dir + "materialized_tbox_abox.nt", header=None, names=['head', 'rel', 'tail'], sep=" ", usecols=range(3)).drop_duplicates(
                keep='first').reset_index(drop=True)
            new_ent2types = get_types_hrt_from_nt(df, self.context_resource)
        if os.path.exists(self.work_dir + "materialized_role_instance.xml"):
            # Konclude realisation has two steps, one is to call realization to get type assertions,
            # another is to query for each role to get new relation assertions
            rel_triples = []
            with open(self.work_dir + "materialized_role_instance.xml", mode='r') as f_r:
                soup = BeautifulSoup(f_r.read(), 'lxml')
                for result_tag in soup.findAll('result'):
                    binding = result_tag.select('binding')
                    if len(binding) == 3:
                        rel_triples.append([binding[0].get_text(), binding[1].get_text(), binding[2].get_text()])
            df_properties = pd.DataFrame(data=rel_triples, columns=['head', 'rel', 'tail'])
            df_properties[['head', 'tail']] = df_properties[['head', 'tail']].applymap(
                lambda x: self.context_resource.ent2id[x] if x in self.context_resource.ent2id else np.nan)  # to int
            df_properties['rel'] = df_properties['rel'].apply(
                lambda x: self.context_resource.op2id[x] if x in self.context_resource.op2id else np.nan)  # to int
            df_properties = df_properties.dropna(how='any').astype('int64')
        return new_ent2types, df_properties


class MaterialisationTrOWL(MaterialisationReasoner):
    def __init__(self, work_dir, context_resource: ContextResources, exclude_rels=[]):
        self.context_resource = context_resource
        self.work_dir = work_dir
        self.exclude_rels = exclude_rels

    def do_materialise(self):
        cmd = f"java -Dtask=TrOWL -Dschema=tbox_abox.nt -Doutput_dir=./ -jar {self.work_dir}TBoxTREAT-1.0.jar"
        os.system(cmd)
        wait_until_file_is_saved(self.work_dir + "materialized_tbox_abox.nt", 60*3)
        return self.parse_result()

    def parse_result(self):
        df_properties = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        df_types = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
        if os.path.exists(self.work_dir + "materialized_tbox_abox.nt"):
            df = pd.read_csv(
                self.work_dir + "materialized_tbox_abox.nt", header=None, names=['head', 'rel', 'tail'], sep=" ", usecols=range(3)).drop_duplicates(
                keep='first').reset_index(drop=True)
            df_types = get_types_hrt_from_nt(df, self.context_resource)
            df_properties = get_rel_hrt_from_nt(df, self.context_resource, self.exclude_rels)
        return df_properties, df_types


def get_rel_hrt_from_nt(df: pd.DataFrame, context_resource: ContextResources, exclude_rels=[]):
    exclusive = [f"<{r}>" for r in exclude_rels]
    exclude_rels.append(RDFTYPE1)
    df_properties = df.query("rel not in @exclusive")
    df_properties = df_properties.apply(lambda x: x.str[1:-1])
    df_properties[['head', 'tail']] = df_properties[['head', 'tail']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df_properties['rel'] = df_properties['rel'].apply(
        lambda x: context_resource.op2id[x] if x in context_resource.op2id else np.nan)  # to int
    df_properties = df_properties.dropna(how='any').astype('int64')
    return df_properties


def get_types_hrt_from_nt(df: pd.DataFrame, context_resource: ContextResources):
    df_types = df.query("rel==@RDFTYPE1")
    # get type dict
    df_types = df_types[['head', 'tail']].apply(lambda x: x.str[1:-1])
    df_types['head'] = df_types[['head']].applymap(
        lambda x: context_resource.ent2id[x] if x in context_resource.ent2id else np.nan)  # to int
    df_types['tail'] = df_types[['tail']].applymap(
        lambda x: context_resource.class2id[x] if x in context_resource.class2id else np.nan)  # to int
    df_types = df_types.dropna(how='any').astype('int64')
    df_types['rel'] = 0
    df_types = df_types[['head', 'rel', 'tail']].astype('int64')
    return df_types


def prepare_konclude_relation_queries(work_dir, exclude_rels):
    sparql_strs = []
    print("preparing role_queries.sparql")
    with open(work_dir + 'AllObjectProperties.txt', mode='r') as fin:
        for l in fin.readlines():
            uri = l.strip()
            if uri in exclude_rels:
                continue
            sparql = f"SELECT Distinct ?x (<{uri}> AS ?relation)  ?y " + "Where { ?x " + f"<{uri}> ?y . " + "} \n"
            sparql_strs.append(sparql)
    with open(work_dir + "role_queries.sparql", mode='w') as fout:
        for s in sparql_strs:
            fout.write(s)
    wait_until_file_is_saved(work_dir + "role_queries.sparql")
    print(f"Saved {work_dir}role_queries.sparql")


def materialize(work_dir, context_resource: ContextResources, reasoner='TrOWL', exclude_rels=[]):
    os.system('../scripts/prepare_materialize.sh ' + work_dir[:-1])
    start_time = datetime.datetime.now()
    if reasoner == 'TrOWL':
        reasoner_func = MaterialisationTrOWL
    else:
        reasoner_func = MaterialisationKonclude
    reasoner_util = reasoner_func(work_dir=work_dir, context_resource=context_resource, exclude_rels=exclude_rels)
    new_type_assertions, new_property_assertions = reasoner_util.do_materialise()
    print(f"The materialisation duration is {datetime.datetime.now() - start_time}")
    return new_property_assertions, new_type_assertions


# return new count
def update_ent2class(context_resource: ContextResources, pred_type_df) -> int:
    old_ent2types = context_resource.entid2classids
    groups = pred_type_df.groupby('head')
    old_ent2types = context_resource.entid2classids
    old_type_count = context_resource.get_type_count()
    for g in groups:
        ent = g[0]
        types = g[1]['tail'].tolist()
        if ent in old_ent2types:
            old_types = set(old_ent2types[ent])
            new_types = set(types)
            old_ent2types.update({ent: list(old_types | new_types)})
    type_count = context_resource.get_type_count()
    new_count = type_count - old_type_count
    return new_count


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


def clean_materialization(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_materialization.sh ' + work_dir)


#
# if __name__ == "__main__":
#     dataset_config = DatasetConfig().get_config('TREAT')
#
#
