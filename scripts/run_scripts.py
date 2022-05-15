import os
from abox_scanner.abox_utils import wait_until_file_is_saved


def run_tbox_scanner(schema_file, work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system(f'../scripts/tbox_Scanner.sh  {schema_file} {work_dir}')


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



