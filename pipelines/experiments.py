from pipeline_C_L_C import c_l_c
from pipeline_C_anyBURL_C import c_anyburl_c
from pipeline_C_E_C import c_e_c
from pipeline_CECMCRC import cecmcrc
from pipeline_CLCMCRC import clcmcac
from scripts import run_scripts
import argparse


class ExpConfig:
    input_dir = ""
    schema_file = ""
    tbox_patterns_dir = ""
    inductive = False
    literal_model = "blp"
    max_epoch = 2
    use_gpu = False

    def setTest(self):
        self.input_dir = "../resources/TEST/"
        self.schema_file = '../resources/NELL/NELL.ontology.nt'
        self.tbox_patterns_dir = "../resources/NELL-patterns/"
        self.inductive = True
        self.literal_model = "blp"
        self.e_max_epoch = 5
        self.l_max_epoch = 5

    def setNELL(self):
        self.input_dir = "../resources/NELL/"
        self.schema_file = '../resources/NELL/NELL.ontology.nt'
        self.tbox_patterns_dir = "../resources/NELL-patterns/"
        self.inductive = True
        self.literal_model = "blp"
        # self.rel_model = "transE"
        self.e_max_epoch = 50
        self.l_max_epoch = 50

    def setTREAT(self):
        self.input_dir = "../resources/treat/"
        self.schema_file = '../resources/treat/tbox.nt'
        self.tbox_patterns_dir = "../resources/treat/tbox_patterns/"
        self.inductive = True
        self.literal_model = "fasttext"
        self.e_max_epoch = 50
        self.l_max_epoch = 50

    def setDBpedia(self):
        pass

    def get_config(self, dataset):
        if dataset == "NELL":
            self.setNELL()
        elif dataset == "TREAT":
            self.setTREAT()
        elif dataset == "TEST":
            self.setTest()
        else:
            self.setDBpedia()
        return self


def producers(dataset="TEST", work_dir="outputs/test/", pipeline="cec", use_gpu=False, loops=2):
    run_scripts.mk_dir(work_dir)
    conf = ExpConfig().get_config(dataset)
    scores = []
    if pipeline == "cac":
        print("CRC pipeline")
        scores = c_anyburl_c(work_dir=work_dir + f"cac_{dataset}/",
                             input_dir=conf.input_dir,
                             schema_file=conf.schema_file,
                             loops=loops,
                             tbox_patterns_dir=conf.tbox_patterns_dir)
    elif pipeline == "cec":
        print("CEC pipeline")
        scores = c_e_c(work_dir=work_dir + f"cec_{dataset}/",
                       input_dir=conf.input_dir,
                       schema_file=conf.schema_file,
                       tbox_patterns_dir=conf.tbox_patterns_dir,
                       loops=loops,
                       epoch=conf.e_max_epoch,
                       use_gpu=use_gpu)
    elif pipeline == "clc":
        print("CLC pipeline")
        scores = c_l_c(work_dir=work_dir + f"clc_{dataset}/",
                       input_dir=conf.input_dir,
                       schema_file=conf.schema_file,
                       tbox_patterns_dir=conf.tbox_patterns_dir,
                       inductive=conf.inductive,
                       epoch=conf.l_max_epoch,
                       loops=loops,
                       model=conf.literal_model)
    elif pipeline == "clcmcac":
        print("clcmcac pipeline")
        scores = clcmcac(work_dir=work_dir + f"clc_{dataset}/",
                         input_dir=conf.input_dir,
                         schema_file=conf.schema_file,
                         tbox_patterns_dir=conf.tbox_patterns_dir,
                         inductive=conf.inductive,
                         epoch=conf.l_max_epoch,
                         loops=loops,
                         model=conf.literal_model)
    with open(work_dir + "experiment.log", encoding='utf-8', mode='w') as out_f:
        for idx, s in enumerate(scores):
            out_f.write(f"loop {idx}:\n")
            for k in s:
                out_f.write(f"{k}: {s[k]} \n")
            out_f.write("-------------")
    out_f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    # dataset="TEST", work_dir="outputs/test/", pipeline="cec", use_gpu=False, loops=2
    parser.add_argument('--dataset', type=str, default="TEST")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--pipeline', type=str, default="cac")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=2)
    args = parser.parse_args()
    producers(dataset=args.dataset,
              work_dir=args.work_dir,
              pipeline=args.pipeline,
              use_gpu=args.use_gpu,
              loops=args.loops)
