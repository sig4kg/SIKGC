import json
from SPARQLWrapper import SPARQLWrapper, JSON
import platform
import log_util
from datetime import datetime
import validators
from tqdm import tqdm
import regex

log = log_util.get_logger('rule_validation')

LOCALHOST = "localhost"
DBPEDIA_GRAPH_PORT = 8890 if platform.system() == 'Linux' else 5002
DBPEDIA_GRAPH_URL = f"http://{LOCALHOST}:{DBPEDIA_GRAPH_PORT}/sparql"

# class Singleton(object):
#     def __init__(self, cls):
#         self._cls = cls
#         self._instance = {}
#     def __call__(self):
#         if self._cls not in self._instance:
#             self._instance[self._cls] = self._cls()
#         return self._instance[self._cls]
#
#
#
# @Singleton
class PredicatesAndRules(object):
    def __init__(self, rule_file):
        self.predicate2rules = read_json_rules(rule_file)

    def get_rules(self, pred, threshold=-1):
        if pred not in self.predicate2rules:
            return []
        if threshold != -1:
            return [rule for rule in self.predicate2rules[pred]
                    if rule['human_confidence'] >= threshold or rule['computed_confidence'] >= threshold]
        else:
            return self.predicate2rules[pred]


def read_json_rules(filename):
    with open(filename, encoding='utf-8', mode='r') as in_f:
        item = json.load(in_f)
        return item


def read_txt_lines(filename):
    with open(filename, encoding='utf-8', mode='r') as in_f:
        lines = in_f.readlines()
        return [line.strip() for line in lines]


def filter_json_rules(rule_filename, predicates_filename, out_filename):
    all_rules = read_json_rules(rule_filename)
    predicates = read_txt_lines(predicates_filename)
    predicate2rules = dict()
    for pred in predicates:
        filtered_rules = [{"ruleId": rule['ruleId'],
                           "predicate": rule["predicate"],
                           "rule_type": rule['rule_type'],
                           "premise": rule['premise'],
                           "conclusion": rule['conclusion'],
                           "premise_triples": rule['premise_triples'],
                           "conclusion_triple": rule['conclusion_triple'],
                           "human_confidence": rule['human_confidence'],
                           "computed_confidence": rule['computed_confidence'],
                           "source": rule['source']
                           } for rule in all_rules if rule['predicate'] == pred and len(rule["premise_triples"]) < 3]
        predicate2rules.update({pred: filtered_rules})
    save_json(predicate2rules, out_filename)
    return predicate2rules


def rulepremise2sparql(rule_in_json, triple):
    tri_clause = ""
    sparql_filter = ""
    tocheck_subj = f"<{triple[0]}> as ?subj"
    tocheck_obj = f"<{triple[2]}> as ?obj"
    for prem_tri in rule_in_json['premise_triples']:
        if isURI(prem_tri['subject']):
            tmp_subj = f"<{prem_tri['subject']}>"
        elif "^^http://www.w3.org/2001/XMLSchema#" in prem_tri['subject']:
            tmp_subj = prem_tri['subject'].split("^^")[0]
        elif regex.match(r'^v[0-9]*$', prem_tri['subject']):
            tmp_subj = '?' + prem_tri['subject']
        else:
            tmp_subj = f"\"{prem_tri['subject']}\""

        if isURI(prem_tri['object']):
            tmp_obj = f"<{prem_tri['object']}>"
        elif "^^http://www.w3.org/2001/XMLSchema#" in prem_tri['object']:
            tmp_obj = prem_tri['object'].split("^^")[0]
        elif regex.match(r'^v[0-9]*$', prem_tri['object']):
            tmp_obj = '?' + prem_tri['object']
        else:
            tmp_obj = f"\"{prem_tri['object']}\""

        if prem_tri['predicate'] not in ['>', '<']:
            tri_clause = tri_clause + f"{tmp_subj} <{prem_tri['predicate']}> {tmp_obj} . "
        else:
            if prem_tri['subject'] == prem_tri['object']:
                print("invalid rule")
                return ""
            sparql_filter = sparql_filter + f"FILTER ({tmp_subj} {prem_tri['predicate']} {tmp_obj}) "
    query_str = f"SELECT DISTINCT {tocheck_subj} {tocheck_obj} FROM <http://dbpedia.org> " \
                "WHERE { " \
                f"{tri_clause}" \
                f"{sparql_filter}" \
                "} LIMIT 10"

    query_str = query_str.replace("\"subject\"", f"<{triple[0]}>").replace("\"object\"", f"<{triple[2]}>")
    return query_str


def run_query(query_str, defaultGraph=""):
    # log.debug("virtuoso query str: " + query_str)
    start = datetime.now()
    if len(defaultGraph) > 0:
        sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL, defaultGraph=defaultGraph)
    else:
        sparql = SPARQLWrapper(DBPEDIA_GRAPH_URL)
    sparql.setTimeout(20)
    sparql.setQuery(query_str)
    sparql.setReturnFormat(JSON)
    records = []
    try:
        response = sparql.query()
        results = response.convert()
        for recd in results["results"]["bindings"]:
            tri = dict()
            tri['subject'] = recd['subj']['value']
            tri['object'] = recd['obj']['value']
            if 'datatype' in recd['obj']:
                tri['datatype'] = recd['obj']['datatype'].split('#')[-1]
            else:
                tri['datatype'] = 'uri'

            records.append(tri)
        response.response.close()
        log.debug(f"sparql time: {(datetime.now() - start).seconds}")
        return records
    except Exception as err:
        log.warning("failed to query virtuoso...")
        log.error(err)
        log.debug(f"sparql time: {(datetime.now() - start).seconds}")
        return records


# False: conflict
# True: likely true
def neg_rule_checking(triple, pred2neg_rules: PredicatesAndRules):
    relation = triple[1]
    neg_rules = pred2neg_rules.get_rules(relation)
    for nr in neg_rules:
        query_str = rulepremise2sparql(nr, triple)
        if query_str == "":
            continue
        record = run_query(query_str)
        if len(record) > 0:
            return False
    return True


def read_json_rows(file):
    d_list = []
    with open(file, encoding='utf-8', mode='r') as in_f:
        for line in in_f:
            item = json.loads(line.strip())
            d_list.append(item)
    return d_list


def save_jsonl(d_list, filename):
    with open(filename, encoding='utf-8', mode='w') as out_f:
        for item in d_list:
            out_f.write(json.dumps(item) + '\n')


def save_json(json_data, filename):
    with open(filename, encoding='utf-8', mode='w') as out_f:
        out_f.write(json.dumps(json_data, indent=4) + '\n')


def isURI(text):
    return validators.url(text)


if __name__ == "__main__":
    filter_json_rules("../outputs/test_rule/dbpedia_neg_rules.json", "../outputs/test_rule/relations.txt", "../outputs/test_rule/dbpedia_neg_politics.json")
    test_tris = read_txt_lines("../outputs/test_rule/all_triples.tsv")
    test_tris = [r.split('\t') for r in test_tris]
    neg_pred2rules = PredicatesAndRules("../outputs/test_rule/dbpedia_neg_politics.json")
    res = []
    count = 0
    for t in tqdm(test_tris):
        # if count == 70:
        is_true = neg_rule_checking(t, neg_pred2rules)
        res.append(is_true)
        # count += 1
    print(f"total triples: {len(res)}; false: {res.count(False)}")