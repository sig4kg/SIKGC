from abc import ABC, abstractmethod
import logging
import pipelines.M
import pipelines.RC
import pipelines.AC
import pipelines.LC
import pipelines.EC


class PipelineRunnerBase(ABC):
    def __init__(self, logger: logging.Logger = None):
        self.letter2block = {
            'M': lambda kwargs: pipelines.M.M(kwargs['context_resource'], kwargs['pipeline_config'], kwargs['logger']),
            'L': lambda kwargs: pipelines.LC.LC(kwargs['context_resource'], kwargs['abox_scanner_scheduler'],
                                                kwargs['pipeline_config'], kwargs['logger']),
            'A': lambda kwargs: pipelines.AC.AC(kwargs['context_resource'], kwargs['abox_scanner_scheduler'],
                                                kwargs['pipeline_config'], kwargs['logger']),
            'E': lambda kwargs: pipelines.EC.EC(kwargs['context_resource'], kwargs['abox_scanner_scheduler'],
                                                kwargs['pipeline_config'], kwargs['logger'])
        }
        self.logger = logger

    def get_block(self, letter: str, **kwargs):
        func = self.letter2block[letter]
        return func(kwargs)

    @abstractmethod
    def create_pipeline(self, *args):
        pass

    @abstractmethod
    def run_pipeline(self, *args):
        pass


def log_score(dict_data, logger:logging.Logger, loop=-1):
    log_str = ""
    if loop >= 0:
        log_str += f"loop {loop}:\n"
    for k in dict_data:
        log_str += f"{k}: {dict_data[k]} \n"
    log_str += "-------------\n"
    logger.log(log_str)


