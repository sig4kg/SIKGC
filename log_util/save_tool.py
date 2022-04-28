import os
from datetime import datetime


def get_cur_time_str():
    date_now = datetime.now().strftime("%m-%d[%H:%M:%S]")
    return date_now


if __name__ == "__main__":
    # print(gen_file_prefix("this_is_my_model."))
    print(get_cur_time_str())