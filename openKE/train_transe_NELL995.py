from openKE.openke.config import Trainer, TripleProducer
from openKE.openke.module.model import TransE
from openKE.openke.module.loss import MarginLoss
from openKE.openke.module.strategy import NegativeSampling
from openKE.openke.data import TrainDataLoader, TestDataLoader
from pathlib import Path

def train(in_path, use_gpu=False):
    # dataloader for training
    train_dataloader = TrainDataLoader(
        in_path=in_path,
        nbatches=100,
        threads=8,
        sampling_mode="normal",
        bern_flag=1,
        filter_flag=1,
        neg_ent=25,
        neg_rel=0)

    # define the model
    transe = TransE(
        ent_tot=train_dataloader.get_ent_tot(),
        rel_tot=train_dataloader.get_rel_tot(),
        dim=200,
        p_norm=1,
        norm_flag=True)

    # define the loss function
    model = NegativeSampling(
        model=transe,
        loss=MarginLoss(margin=5.0),
        batch_size=train_dataloader.get_batch_size()
    )

    # train the model
    trainer = Trainer(model=model, data_loader=train_dataloader, train_times=500, alpha=1.0, use_gpu=use_gpu)
    trainer.run()
    out_path = Path(in_path + '../checkpoint/transe.ckpt')
    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=False)
    transe.save_checkpoint(in_path + '../checkpoint/transe.ckpt')
    # transe.save_checkpoint(out_dir + '/transe.ckpt')


def produce(in_path, out_file, threshold=0.5, use_gpu=False):
    # dataloader for test
    test_dataloader = TestDataLoader(in_path, "link")
    transe = TransE(
        ent_tot=test_dataloader.get_ent_tot(),
        rel_tot=test_dataloader.get_rel_tot(),
        dim=200,
        p_norm=1,
        norm_flag=True)
    # test the model
    transe.load_checkpoint(in_path + '../checkpoint/transe.ckpt')
    producer = TripleProducer(model=transe, data_loader=test_dataloader, use_gpu=use_gpu, output_file=out_file)
    producer.produce_triples(type_constrain=False, threshold=threshold)


if __name__ == "__main__":
    train("../resources/NELL-995/")

