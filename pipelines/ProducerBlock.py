from abc import ABC, abstractmethod
import pandas as pd
from pipelines.exp_config import *


class ProducerBlock(ABC):
    @abstractmethod
    def produce(self, *args):
        pass

    @abstractmethod
    def collect_result(self, *args):
        pass


class PipelineConfig:
    work_dir = "../outputs/test/"
    blp_config = {}
    inductive = False
    loops = 1
    use_gpu = False
    input_dir = "../resources/TEST/"
    schema_file = '../resources/NELL/tbox.nt'
    tbox_patterns_dir = "../resources/NELL-patterns/"
    e_max_epoch = 2
    exclude_rels = []
    schema_in_nt = '../resources/TEST/tbox_dllite.nt'
    dataset = ""
    reasoner = "Konclude"

    def set_config(self, blp_config: {}, data_config: DatasetConfig, dataset, loops, work_dir, use_gpu):
        self.blp_config = blp_config
        self.work_dir = work_dir
        self.loops = loops
        self.dataset = dataset
        self.input_dir = data_config.input_dir
        self.schema_file = data_config.schema_file
        self.tbox_patterns_dir = data_config.tbox_patterns_dir
        self.e_max_epoch = data_config.e_max_epoch
        self.exclude_rels = data_config.exclude_rels
        self.schema_in_nt = data_config.schema_in_nt
        self.use_gpu = use_gpu
        self.inductive = blp_config['inductive']
        return self

    def __iter__(self):
        return self.__dict__.items().__iter__()
