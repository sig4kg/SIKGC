from abc import ABC, abstractmethod
import pandas as pd
from pipelines.exp_config import *
import pipelines.M
import pipelines.RC
import pipelines.AC
import pipelines.LC
import pipelines.EC


class PipelineRunnerBase(ABC):
    letter2block = {
        'M': pipelines.M.M,
        'L': pipelines.LC.LC,
        'A': pipelines.AC.AC,
        'E': pipelines.EC.EC
    }

    @abstractmethod
    def create_pipeline(self, *args):
        pass

    @abstractmethod
    def run_pipeline(self, *args):
        pass


def log_score(dict_data, log_file, loop=-1):
    with open(log_file, encoding='utf-8', mode='a+') as out_f:
        if loop >= 0:
            out_f.write(f"loop {loop}:\n")
        for k in dict_data:
            out_f.write(f"{k}: {dict_data[k]} \n")
        out_f.write("-------------\n")
    out_f.close()


