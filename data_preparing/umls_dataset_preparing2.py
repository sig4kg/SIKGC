import types
import pandas as pd
from owlready2 import *
from tqdm import tqdm
from difflib import SequenceMatcher
import os
import os.path as osp
from umls_dataset_preparing import *


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


prefix = "http://umls.org/onto.owl"


def convert2abox_nt(work_dir, text2Obj, cid2phrase, cid2types):
    pd_train = pd.read_csv(work_dir + "train.txt", header=None, names=['head', 'rel', 'tail'], sep="\t", error_bad_lines=False, engine="python")
    pd_dev = pd.read_csv(work_dir + "valid.txt", header=None, names=['head', 'rel', 'tail'], sep="\t", error_bad_lines=False, engine="python")
    pd_test = pd.read_csv(work_dir + "test.txt", header=None, names=['head', 'rel', 'tail'], sep="\t", error_bad_lines=False, engine="python")
    all_triples = pd.concat([pd_test, pd_dev, pd_train]).drop_duplicates(keep='first')
    all_ents = pd.concat([all_triples['head'], all_triples['tail']]).drop_duplicates(keep='first').to_list()
    ent2cid = dict()
    ent2text = dict()
    ent2score = dict()
    not_found = []
    for ent in tqdm(all_ents):
        found = False
        ent_phrase = ent.replace("_", " ")
        for cid, names in cid2phrase.items():
            ent2text.update({f"{prefix}/{ent}": ent_phrase})
            for name in names:
                possible_name_lower = name.lower()
                similarity = similar(ent_phrase, possible_name_lower)
                if (ent not in ent2score or similarity > ent2score[ent]) and similarity > 0.75:
                    ent2cid.update({ent: cid})
                    ent2score.update({ent: similarity})
                if ent in ent2score and ent2score[ent] > 0.9:
                    found = True
                    print(f"{ent}: {','.join(cid2phrase[cid])}\n")
                    break
            if found:
                break
        if not found:
            not_found.append(ent)

    print(' '.join(not_found))
    with open(work_dir + 'entity2text.txt', 'w') as f:
        for ent, text in ent2text.items():
            f.write(f"{ent}\t{text}\n")

    with open(work_dir + 'entity2type.txt', 'w') as f:
        for ent, cid in ent2cid.items():
            f.write(f"{prefix}/{ent}\t{';'.join(cid2types[cid])}\n")

    all_triples[['head', 'tail']] = all_triples[['head', 'tail']].applymap(lambda x: f"{prefix}/{x}")
    all_triples[['rel']] = all_triples[['rel']].applymap(lambda x: text2Obj[x].iri)
    all_triples.to_csv(osp.join(work_dir, f'abox_hrt_uri.txt'), header=False, index=False, sep='\t')


# def tmp_fix(work_dir):
#     fixed = []
#     with open(work_dir + 'entity2type.txt', 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             items = line.strip().split('\t')
#             ent_phrase = items[0]
#             fixed.append(f"{prefix}/{ent_phrase}\t{items[1]}\n")
#     with open(work_dir + 'entity2type2.txt', 'w') as f:
#         f.writelines(fixed)

def fix_tmp(type_dir, ent_dir):
    to_fix = 'clinical_attribute body_location_or_region disease_or_syndrome chemical_viewed_functionally mental_or_behavioral_dysfunction human_caused_phenomenon_or_process genetic_function professional_society organism_function pathologic_function experimental_model_of_disease neuroreactive_substance_or_biogenic_amine biologically_active_substance body_space_or_junction acquired_abnormality physiologic_function molecular_biology_research_technique professional_or_occupational_group organ_or_tissue_function fully_formed_anatomical_structure daily_or_recreational_activity element_ion_or_isotope injury_or_poisoning body_part_organ_or_organ_component nucleic_acid_nucleoside_or_nucleotide chemical_viewed_structurally individual_behavior hazardous_or_poisonous_substance cell_or_molecular_dysfunction biomedical_or_dental_material indicator_reagent_or_diagnostic_aid organism_attribute group_attribute therapeutic_or_preventive_procedure rickettsia_or_chlamydia health_care_related_organization drug_delivery_device natural_phenomenon_or_process self_help_or_relief_organization environmental_effect_of_humans gene_or_genome research_device machine_activity idea_or_concept patient_or_disabled_group governmental_or_regulatory_activity phenomenon_or_process biomedical_occupation_or_discipline functional_concept spatial_concept regulation_or_law temporal_concept'
    to_fix = to_fix.split(' ')
    type_text2uri = dict()
    with open(type_dir + 'entity2text1.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            items = line.strip().split('\t')
            type_phrase = items[1]
            type_iri = items[0]
            type_text2uri.update({type_phrase: type_iri})
    ent2types = {}
    with open(ent_dir + 'entity2type.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            items = line.strip().split('\t')
            ent2types.update({items[0]: items[1].split(';')})
    for ent in to_fix:
        found = False
        ent_phrase = ent.replace('_', ' ')
        for type_text, type_iri in type_text2uri.items():
            if similar(ent_phrase.lower(), type_text.lower()) > 0.9:
                if ent in ent2types:
                    ent2types[ent] = [type_iri]
                else:
                    ent2types.update({f"{prefix}/{ent}": [type_iri]})
                found = True
                break
        if not found:
            print("Not found: " + ent)
    with open(ent_dir + 'entity2type_fixed.txt', 'w') as f:
        for ent, type in ent2types.items():
            f.write(f"{ent}\t{';'.join(type)}\n")



if __name__ == "__main__":
    # gp2clz = read_groups("../resources/UMLS/SemGroups.txt")
    # tmp_chunks = read_tbox_rrf("../resources/UMLS/SU")
    # phrase2typeobj, tid2obj = convert_tbox(tmp_chunks, gp2clz, "../resources/UMLS/")
    # cid2name = convert_cid2name("../resources/UMLS/MRCONSO.RRF")
    # cid2types = convert_type_assertions("../resources/UMLS/MRSTY.RRF", tid2obj)
    # convert2abox_nt("../resources/umls2/", phrase2typeobj, cid2name, cid2types)
    fix_tmp("../resources/UMLS/", "../resources/umls2/")

