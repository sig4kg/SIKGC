from pipeline_C_L_C import c_l_c
from pipeline_C_anyBURL_C import c_anyburl_c
from pipeline_C_E_C import c_e_c
from pipeline_CECMCRC import cecmcrc
from pipeline_CLCMCRC import clcmcac
from scripts import run_scripts


class ExpConfig:
    input_dir = ""
    schema_file = ""
    tbox_patterns_dir = ""
    inductive = False
    literal_model = "blp"
    max_epoch=2
    use_gpu=False

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
        else:
            self.setDBpedia()
        return self


def single_producer(dataset, work_dir, use_gpu=False, loops=2):
    run_scripts.mk_dir(work_dir)
    conf = ExpConfig().get_config(dataset)
    print("CRC pipeline")
    scores1 = c_anyburl_c(work_dir=work_dir + f"cac_{dataset}/",
                          input_dir=conf.input_dir,
                          schema_file=conf.schema_file,
                          tbox_patterns_dir=conf.tbox_patterns_dir)

    print("CEC pipeline")
    scores2 = c_e_c(work_dir=work_dir + f"cec_{dataset}/",
                    input_dir=conf.input_dir,
                    schema_file=conf.schema_file,
                    tbox_patterns_dir=conf.tbox_patterns_dir,
                    loops=loops,
                    epoch=conf.e_max_epoch,
                    use_gpu=use_gpu)

    print("CLC pipeline")
    scores3 = c_l_c(work_dir=work_dir + f"clc_{dataset}/",
                    input_dir=conf.input_dir,
                    schema_file=conf.schema_file,
                    tbox_patterns_dir=conf.tbox_patterns_dir,
                    inductive=conf.inductive,
                    epoch=conf.l_max_epoch,
                    loops=loops,
                    model=conf.literal_model)
    with open(work_dir + "experiment_single.log", encoding='utf-8', mode='w') as out_f:
        out_f.write("scores: f_correctness, f_coverage, f_h")
        for idx, s in enumerate(scores1):
            out_f.write(f"CRC loop {idx}: {s[0]}\t{s[1]}\t{s[2]}\n")
        for idx, s in enumerate(scores2):
            out_f.write(f"CEC loop {idx}: {s[0]}\t{s[1]}\t{s[2]}\n")
        for idx, s in enumerate(scores3):
            out_f.write(f"CLC loop {idx}: {s[0]}\t{s[1]}\t{s[2]}\n")
    out_f.close()



def combined_producers(dataset, work_dir, loops=2):
    conf = ExpConfig().get_config(dataset)
    print("clcmcac pipeline")
    scores = clcmcac(work_dir=work_dir + f"clc_{dataset}/",
            input_dir=conf.input_dir,
            schema_file=conf.schema_file,
            tbox_patterns_dir=conf.tbox_patterns_dir,
            inductive=conf.inductive,
            epoch=conf.l_max_epoch,
            loops=loops,
            model=conf.literal_model)
    with open(work_dir + "experiment_single.log", encoding='utf-8', mode='w') as out_f:
        out_f.write("scores: f_correctness, f_coverage, f_h")
        for idx, s in enumerate(scores):
            out_f.write(f"CRC loop {idx}: {s[0]}\t{s[1]}\t{s[2]}\n")
    out_f.close()


if __name__ == "__main__":
    single_producer("NELL", "../outputs/single/")