from pathlib import Path
import os
import time


def init_dir(work_dir):
    out_path = Path(work_dir)
    if not out_path.exists():
        out_path.mkdir(exist_ok=False)


def save_to_file(text, out_filename, mode='w'):
    out_path = Path(out_filename)
    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=False)
    with open(out_path, encoding='utf-8', mode=mode) as out_f:
        out_f.write(text)


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

