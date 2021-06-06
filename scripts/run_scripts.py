import os
from abox_scanner.abox_utils import wait_until_file_is_saved


def run_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    wait_until_file_is_saved(work_dir + "/ideal.data.txt", 60)
    wait_until_file_is_saved(work_dir + "/dlv.bin", 10)
    wait_until_file_is_saved(work_dir + "/rumis-1.0.jar", 10)
    os.system('../scripts/run_rumis.sh ' + work_dir)


def clean_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('../scripts/rumis_clean.sh ' + work_dir)


def clean_tranE(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('echo ../scripts/transE_clean.sh')
    os.system('../scripts/transE_clean.sh ' + work_dir)


def delete_file(file_path):
    os.system("rm " + file_path)

def gen_pred_transE(work_dir):
    wait_until_file_is_saved(f"{work_dir}train/train2id.txt", 60)
    os.system(f"cp {work_dir}train/train2id.txt {work_dir}train/test2id.txt")
    os.system(f"cp ../resources/NELL-995/type_constrain.txt {work_dir}train/type_constrain.txt")
    os.system(f"cp {work_dir}train/train2id.txt {work_dir}train/valid2id.txt")


def run_materialization(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]


clean_tranE("../outputs/ctc/")