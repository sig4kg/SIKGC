import os
import os.path as osp
from pathlib import Path
from torch.utils.data import DataLoader,Dataset,RandomSampler, SequentialSampler
from abox_scanner.ContextResources import ContextResources
from blp.extend_models import *
from sklearn.metrics import accuracy_score, balanced_accuracy_score
import torch
import numpy as np
import utils
import pandas as pd
from collections import defaultdict
from sklearn.linear_model import LogisticRegression
from collections import Counter
from torch.nn import BCELoss
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42


class TypeDataset(Dataset):
    def __init__(self, ent_emb, ent2idx, ent_ids, type_ids):
        self.ent_emb = ent_emb
        self.ent_ids = ent_ids
        self.labels = type_ids
        self.ent2idx = ent2idx
        # with open(in_file) as f:
        #     for line in f:
        #         items = line.strip().split()
        #         entity = items[0]
        #         ent_types = items[1:]
        #         entity_id = ent_ids[entity]
        #         entity_idx = ent2idx[entity_id]
        #         idx.append(entity_idx)
        #         labels.append(class2labels(ent_types))

    def __getitem__(self, item):
        x_id = self.ent2idx[item]
        x = self.ent_emb[x_id]
        y = np.array(item)
        y = torch.FloatTensor(y)
        return x, y

    def __len__(self):
        return len(self.ent_ids)


class TypeDataModule(pl.LightningDataModule):
    def __init__(self,x_tr,y_tr,x_val,y_val,x_test,y_test,ent_emb, ent2idx, batch_size=16):
        super().__init__()
        self.tr_ent = x_tr
        self.tr_label = y_tr
        self.val_ent = x_val
        self.val_label = y_val
        self.test_ent = x_test
        self.test_label = y_test
        self.ent_emb = ent_emb
        self.ent2idx = ent2idx

    def setup(self):
        self.train_dataset = TypeDataset(ent_emb=self.ent_emb, ent2idx=self.ent2idx, ent_ids=self.tr_ent, labels=self.tr_label)
        self.val_dataset  = TypeDataset(ent_emb=self.ent_emb, ent2idx=self.ent2idx, ent_ids=self.dev_ent, labels=self.dev_label)
        self.test_dataset  = TypeDataset(ent_emb=self.ent_emb, ent2idx=self.ent2idx, ent_ids=self.test_ent, labels=self.test_label)

    def train_dataloader(self):
        return DataLoader(self.train_dataset,batch_size=self.batch_size,shuffle=True, num_workers=2)

    def val_dataloader(self):
        return DataLoader(self.val_dataset,batch_size= 16)

    def test_dataloader(self):
        return DataLoader(self.test_dataset,batch_size= 16)



class NodeClassifier(pl.LightningModule):
    # Set up the classifier
    def __init__(self, emb_dim=100, n_classes=50, steps_per_epoch=None,n_epochs=3, lr=2e-5):
        super().__init__()
        self.classifier = nn.Linear(emb_dim, n_classes)
        self.steps_per_epoch = steps_per_epoch
        self.n_epochs = n_epochs
        self.lr = lr
        self.criterion = nn.BCEWithLogitsLoss()

    # def forward(self, ent_emb):
    #     output = self.classifier(ent_emb)
    #     return output

    def training_step(self,batch, batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('train_loss',loss , prog_bar=True,logger=True)
        return {"loss" :loss, "predictions":outputs, "labels": labels }

    def validation_step(self,batch,batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        labels = batch['label']
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('val_loss',loss , prog_bar=True,logger=True)
        return loss

    def test_step(self,batch,batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        labels = batch['label']
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('test_loss',loss , prog_bar=True,logger=True)
        return loss

    def configure_optimizers(self):
        optimizer = AdamW(self.parameters() , lr=self.lr)
        warmup_steps = self.steps_per_epoch//3
        total_steps = self.steps_per_epoch * self.n_epochs - warmup_steps
        scheduler = get_linear_schedule_with_warmup(optimizer,warmup_steps,total_steps)
        return [optimizer], [scheduler]


def split_data(context_resource: ContextResources, num=50):
    all_classes = [i for cls in context_resource.entid2classids.values() for i in cls]
    top_n = Counter(all_classes).most_common(num)
    top_n_tags = [i[0] for i in top_n]
    x = []
    y = []
    for i in context_resource.entid2classids:
        temp = []
        for t in context_resource.entid2classids[i]:
            if t in top_n_tags:
                temp.append(t)
        if len(temp) > 0:
            x.append(i)
            y.append(temp)
    mlb = MultiLabelBinarizer()
    yt = mlb.fit_transform(top_n_tags)
    print("node classification sample data: ")
    # Getting a sense of how the tags data looks like
    print(yt[0])
    print(mlb.inverse_transform(yt[0].reshape(1,-1)))
    print(mlb.classes_)
    # First Split for Train and Test
    x_train,x_dev,y_train,y_dev = train_test_split(x, yt, test_size=0.1, random_state=RANDOM_SEED,shuffle=True)
    print(f"length train: {str(x_train)}, length dev: {str(y_dev)}")
    return x_train,x_dev,y_train,y_dev

def type_train_and_pred():
    # Initialize the parameters that will be use for training
    N_EPOCHS = 12
    BATCH_SIZE = 32
    MAX_LEN = 300
    LR = 2e-05
    # Instantiate and set up the data_module
    Tdata_module = TypeDataModule(x_tr,y_tr,x_val,y_val,x_test,y_test, ent_emb, ent2idx)
    Tdata_module.setup()

    # Instantiate the classifier model
    steps_per_epoch = len(x_tr)//BATCH_SIZE
    model = NodeClassifier(n_classes=10, steps_per_epoch=steps_per_epoch,n_epochs=N_EPOCHS,lr=LR)
    # saves a file like: input/QTag-epoch=02-val_loss=0.32.ckpt
    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',# monitored quantity
        filename='type-{epoch:02d}-{val_loss:.2f}',
        save_top_k=2, #  save the top 3 models
        mode='min', # mode of the monitored quantity  for optimization
    )
    # Instantiate the Model Trainer
    trainer = pl.Trainer(max_epochs=N_EPOCHS, gpus=1, callbacks=[checkpoint_callback], progress_bar_refresh_rate=30)
    # Train the Classifier Model
    trainer.fit(model, Tdata_module)
    trainer.test(model, datamodule=Tdata_module)




def node_classification(dataset, checkpoint):
    ent_emb = torch.load(f'output/ent_emb-{checkpoint}.pt', map_location='cpu')
    if isinstance(ent_emb, tuple):
        ent_emb = ent_emb[0]

    ent_emb = ent_emb.squeeze().numpy()
    num_embs, emb_dim = ent_emb.shape
    print(f'Loaded {num_embs} embeddings with dim={emb_dim}')

    emb_ids = torch.load(f'output/ents-{checkpoint}.pt', map_location='cpu')
    ent2idx = utils.make_ent2idx(emb_ids, max_ent_id=emb_ids.max()).numpy()
    maps = torch.load(f'data/{dataset}/maps.pt')
    ent_ids = maps['ent_ids']
    class2labels = defaultdict(lambda: len(class2labels))

    splits = ['train', 'dev', 'test']
    split_2data = dict()
    for split in splits:
        with open(f'data/{dataset}/{split}-ents-class.txt') as f:
            idx = []
            labels = []
            for line in f:
                entity, ent_class = line.strip().split()
                entity_id = ent_ids[entity]
                entity_idx = ent2idx[entity_id]
                idx.append(entity_idx)
                labels.append(class2labels[ent_class])

            x = ent_emb[idx]
            y = np.array(labels)
            split_2data[split] = (x, y)

    x_train, y_train = split_2data['train']
    x_dev, y_dev = split_2data['dev']
    x_test, y_test = split_2data['test']

    best_dev_metric = 0.0
    best_c = 0
    for k in range(-4, 2):
        c = 10 ** -k
        model = LogisticRegression(C=c, multi_class='multinomial',
                                   max_iter=1000)
        model.fit(x_train, y_train)

        dev_preds = model.predict(x_dev)
        dev_acc = accuracy_score(y_dev, dev_preds)
        print(f'{c:.3f} - {dev_acc:.3f}')

        if dev_acc > best_dev_metric:
            best_dev_metric = dev_acc
            best_c = c

    print(f'Best regularization coefficient: {best_c:.4f}')
    model = LogisticRegression(C=best_c, multi_class='multinomial',
                               max_iter=1000)
    x_train_all = np.concatenate((x_train, x_dev))
    y_train_all = np.concatenate((y_train, y_dev))
    model.fit(x_train_all, y_train_all)

    for metric_fn in (accuracy_score, balanced_accuracy_score):
        train_preds = model.predict(x_train_all)
        train_metric = metric_fn(y_train_all, train_preds)

        test_preds = model.predict(x_test)
        test_metric = metric_fn(y_test, test_preds)

        print(f'Train {metric_fn.__name__}: {train_metric:.3f}')
        print(f'Test {metric_fn.__name__}: {test_metric:.3f}')