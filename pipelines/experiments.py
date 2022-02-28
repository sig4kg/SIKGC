from pipeline_C_L_C import c_l_c
from pipeline_C_anyBURL_C import c_anyburl_c
from pipeline_C_E_C import c_e_c
from pipeline_C_Rumis_C import c_rumis_c
from pipeline_CECMCRC import cecmcrc
from pipeline_CLCMCAC import clcmcac
from pipeline_CACMCLC import cacmclc
from pipeline_CACMCEC import cacmcec
from pipeline_CECMCAC import cecmcac
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
        self.e_max_epoch = 2
        self.l_max_epoch = 2

    def setNELL(self):
        self.input_dir = "../resources/NELL/"
        self.schema_file = '../resources/NELL/NELL.ontology.nt'
        self.tbox_patterns_dir = "../resources/NELL-patterns/"
        self.inductive = True
        self.literal_model = "blp"
        # self.rel_model = "transE"
        self.e_max_epoch = 500
        self.l_max_epoch = 50

    def setTREAT(self):
        self.input_dir = "../resources/TREAT/"
        self.schema_file = '../resources/TREAT/tbox.nt'
        self.tbox_patterns_dir = "../resources/TREAT/tbox_patterns/"
        self.inductive = False
        self.literal_model = "fasttext"
        self.e_max_epoch = 200
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


def producers(dataset="TEST", work_dir="outputs/test/", pipeline="cec", use_gpu=False, loops=3):
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
    elif pipeline == "crc":
        print("CRC pipeline")
        scores = c_rumis_c(work_dir=work_dir + f"crc_{dataset}/",
                           input_dir=conf.input_dir,
                           schema_file=conf.schema_file,
                           loops=loops,
                           tbox_patterns_dir=conf.tbox_patterns_dir)
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
    elif pipeline == "cacmclc":
        print("cacmclc pipeline")
        scores = cacmclc(work_dir=work_dir + f"clc_{dataset}/",
                         input_dir=conf.input_dir,
                         schema_file=conf.schema_file,
                         tbox_patterns_dir=conf.tbox_patterns_dir,
                         inductive=conf.inductive,
                         epoch=conf.l_max_epoch,
                         loops=loops,
                         model=conf.literal_model)
    elif pipeline == "cacmcec":
        print("cacmcec pipeline")
        scores = cacmcec(work_dir=work_dir + f"clc_{dataset}/",
                         input_dir=conf.input_dir,
                         schema_file=conf.schema_file,
                         tbox_patterns_dir=conf.tbox_patterns_dir,
                         epoch=conf.l_max_epoch,
                         loops=loops,
                         use_gpu=conf.use_gpu)
    elif pipeline == "cecmcac":
        print("cecmcac pipeline")
        scores = cecmcac(work_dir=work_dir + f"clc_{dataset}/",
                         input_dir=conf.input_dir,
                         schema_file=conf.schema_file,
                         tbox_patterns_dir=conf.tbox_patterns_dir,
                         epoch=conf.l_max_epoch,
                         loops=loops,
                         use_gpu=conf.use_gpu)
    elif pipeline == "cecmcrc":
        print("cecmcrc pipeline")
        scores = cecmcrc(work_dir=work_dir + f"clc_{dataset}/",
                         input_dir=conf.input_dir,
                         schema_file=conf.schema_file,
                         tbox_patterns_dir=conf.tbox_patterns_dir,
                         epoch=conf.e_max_epoch,
                         loops=loops,
                         use_gpu=conf.use_gpu)
    else:
        print("Unsupported pipeline, please use any of these: cac, cec, crc, cm, cecmcrc, clcmcac.")
        pass
    with open(work_dir + f"{pipeline}_{dataset}.log", encoding='utf-8', mode='w') as out_f:
        for idx, s in enumerate(scores):
            out_f.write(f"loop {idx}:\n")
            for k in s:
                out_f.write(f"{k}: {s[k]} \n")
            out_f.write("-------------\n")
    out_f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="experiment settings")
    # dataset="TEST", work_dir="outputs/test/", pipeline="cec", use_gpu=False, loops=2
    parser.add_argument('--dataset', type=str, default="TREAT")
    parser.add_argument('--work_dir', type=str, default="../outputs/test/")
    parser.add_argument('--pipeline', type=str, default="cecmcac")
    parser.add_argument('--use_gpu', type=bool, default=False)
    parser.add_argument('--loops', type=int, default=3)
    args = parser.parse_args()
    producers(dataset=args.dataset,
              work_dir=args.work_dir,
              pipeline=args.pipeline,
              use_gpu=args.use_gpu,
              loops=args.loops)
