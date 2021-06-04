import os


def run_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('./run_rumis.sh ' + work_dir)


def clean_rumis(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('./rumis_clean.sh ' + work_dir)


def clean_tranE(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
    os.system('./transE_clean.sh ' + work_dir)


def run_materialization(work_dir):
    if work_dir[-1] == '/':
        work_dir = work_dir[:-1]
