from pathlib import Path
import os
import time
import pandas as pd


def init_dir(work_dir):
    out_path = Path(work_dir)
    if not out_path.exists():
        os.makedirs(work_dir, exist_ok=False)


def save_list_to_file(d_list, out_filename, mode='w'):
    out_file = Path(out_filename)
    if not out_file.parent.exists():
        os.makedirs(out_file.parent, exist_ok=False)

    with open(out_filename, encoding='utf-8', mode=mode) as out_f:
        for item in d_list:
            out_f.write(item + '\n')
        out_f.close()

def save_to_file(text, out_filename, mode='w'):
    out_path = Path(out_filename)
    if not out_path.parent.exists():
        os.makedirs(out_path.parent, exist_ok=False)
    with open(out_path, encoding='utf-8', mode=mode) as out_f:
        out_f.write(text)


def does_file_exist(file_path):
    return os.path.exists(file_path)


def wait_until_file_is_saved(file_path: str, timeout_sec=10) -> bool:
    time_counter = 0
    interval = int(timeout_sec / 10) if timeout_sec > 10 else 1
    print(f"waiting for saving {file_path} ...")
    while not os.path.exists(file_path):
        time.sleep(interval)
        time_counter += interval
        # print(f"waiting {time_counter} sec.")
        if time_counter > timeout_sec:
            # print(f"saving {file_path} timeout")
            break
    is_saved = os.path.exists(file_path)
    if is_saved:
        print(f"{file_path} has been saved.")
    else:
        print(f"saving {file_path} timeout")
    return is_saved


def read_hrt_2_hrt_int_df(hrt_file):
    if does_file_exist(hrt_file):
        df = pd.read_csv(
            hrt_file, header=None, names=['head', 'rel', 'tail'], sep="\t")
    else:
        df = pd.DataFrame(data=[], columns=['head', 'rel', 'tail'])
    return df


def write_hrt_df(hrt_df, hrt_file):
    hrt_df.to_csv(hrt_file, header=False, index=False, sep='\t')


def read_type_dict(dict_file):
    r_dict = dict()
    with open(dict_file, mode='r') as f:
        for l in f.readlines():
            items = l.strip().split("\t")
            r_dict.update({int(items[0]): [int(c) for c in items[1:]]})
    return r_dict


def write_type_dict(t_dict,  dict_file):
    content = ""
    for ent in t_dict:
        content = content + f"{str(ent)}\t" + '\t'.join([str(c) for c in t_dict[ent]]) + "\n"
    with open(dict_file, mode='w') as f:
        f.write(content)