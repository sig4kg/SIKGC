import os
from abox_scanner.abox_utils import wait_until_file_is_saved


def run_tbox_scanner(schema_file, work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system(f'../scripts/tbox_Scanner.sh  {schema_file} {work_dir}')

def run_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/run_rumis.sh ' + work_dir)
    wait_until_file_is_saved(work_dir + "/ideal.data.txt", 60)
    wait_until_file_is_saved(work_dir + "/dlv.bin", 10)
    wait_until_file_is_saved(work_dir + "/rumis-1.0.jar", 10)


def learn_anyburl(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/run_anyburl.sh ' + work_dir)
    wait_until_file_is_saved(work_dir + "/rules/alpha-100", 60)


def predict_with_anyburl(work_dir):
    print("Predicting via AnyBURL...")
    os.system(f"java -Xmx10G -cp {work_dir}/AnyBURL-JUNO.jar de.unima.ki.anyburl.Apply {work_dir}/config-apply.properties")
    wait_until_file_is_saved(work_dir + "/predictions/alpha-100_plog", 60)
    print("Evaluating AnyBURL...")
    os.system(f"java -Xmx10G -cp {work_dir}/AnyBURL-JUNO.jar de.unima.ki.anyburl.Eval {work_dir}/config-eval.properties")


def clean_anyburl(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_anyburl.sh ' + work_dir)


def clean_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_rumis.sh ' + work_dir)


def clean_tranE(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('echo ../scripts/clean_transE.sh')
    os.system('../scripts/clean_transE.sh ' + work_dir)


def clean_blp(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('echo ../scripts/clean_blp.sh')
    os.system('../scripts/clean_blp.sh ' + work_dir)


def clean_materialization(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/clean_materialization.sh ' + work_dir)


def run_materialization(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/run_materialize.sh ' + work_dir)
    wait_until_file_is_saved(f"{work_dir}/materialized_tbox_abox.nt")

def to_dllite(schema_file, work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/to_dllite.sh ' + schema_file + ' ' + work_dir)
    wait_until_file_is_saved(f"{work_dir}/tbox_dllite.ttl")

def delete_file(file_path):
    os.system("rm " + file_path)


def delete_dir(dir):
    cmd = f'[ -d {dir} ] && rm -rf {dir}'
    os.system(cmd)


def mk_dir(dir):
    os.system(f'[ ! -d "{dir}" ] && mkdir {dir}')


def prepare_blp(source_dir, work_dir):
    os.system(f"cp {source_dir}entity2text.txt {work_dir}entity2text.txt")
    os.system(f"cp {source_dir}entity2longtext.txt {work_dir}entity2longtext.txt")
    os.system(f"cp {source_dir}entity2type.txt {work_dir}entity2type.txt")
    os.system(f"cp {source_dir}relation2text.txt {work_dir}relation2text.txt")
    wait_until_file_is_saved(f"{work_dir}all_triples.tsv", 120)
