from pipelines.exp_config import DatasetConfig


class PipelineConfig:
    work_dir = "../outputs/test/"
    blp_config = {}
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
    pred_type = False
    parallel = False
    pipeline = ""

    def set_blp_config(self, blp_config: {}):
        self.blp_config = blp_config
        return self

    def set_data_config(self, data_config: DatasetConfig):
        self.input_dir = data_config.input_dir
        self.schema_file = data_config.schema_file
        self.tbox_patterns_dir = data_config.tbox_patterns_dir
        self.e_max_epoch = data_config.e_max_epoch
        self.exclude_rels = data_config.exclude_rels
        self.schema_in_nt = data_config.schema_in_nt
        return self

    def set_pipeline_config(self,
                            dataset,
                            loops,
                            work_dir,
                            use_gpu,
                            pred_type,
                            parallel,
                            pipeline,
                            reasoner):
        self.work_dir = work_dir
        self.loops = loops
        self.dataset = dataset
        self.use_gpu = use_gpu
        self.pred_type = pred_type
        self.reasoner = reasoner
        self.parallel = parallel
        self.pipeline = pipeline
        return self

    def __iter__(self):
        return self.__dict__.items().__iter__()
