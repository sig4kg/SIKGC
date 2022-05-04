from torch.utils.data import DataLoader, Dataset, SequentialSampler
from transformers import get_linear_schedule_with_warmup
from torch.optim import Adam
from abox_scanner.ContextResources import ContextResources
from blp.extend_models import *
from sklearn.metrics import accuracy_score, balanced_accuracy_score
import torch
import numpy as np
import utils
import pandas as pd
from collections import Counter
from torch.nn import BCELoss
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from sklearn import metrics


class DataTransformer():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.x_tr = []
        self.y_tr = []
        self.x_val = []
        self.y_val = []
        self.x_test = []
        self.y_test = []
        self.x = []
        self.y = []
        self.mlb = MultiLabelBinarizer()
        self.num_labels = 0
        self.all_classes = set()

    def data_transform(self):
        x = []
        y = []

        def read_classes(in_file):
            with open(in_file) as f:
                for line in f:
                    items = line.strip().split()
                    ent = items[0]
                    ent_types = items[1:]
                    x.append(ent)
                    y.append(ent_types)
                    self.all_classes.update(ent_types)
                return len(x)

        train_count = read_classes(self.data_dir + "type_train.txt")
        dev_count = read_classes(self.data_dir + "type_dev.txt")
        test_count = read_classes(self.data_dir + "type_test.txt")
        yt = self.mlb.fit_transform(y)
        print("node classification sample data: ")
        # Getting a sense of how the tags data looks like
        print(yt[0])
        print(self.mlb.inverse_transform(yt[0].reshape(1, -1)))
        print(self.mlb.classes_)
        self.x_tr = x[:train_count]
        self.y_tr = yt[:train_count]
        self.x_val = x[train_count: train_count + dev_count]
        self.y_val = yt[train_count: train_count + dev_count]
        self.x_test = x[train_count + dev_count:]
        self.y_test = yt[train_count + dev_count:]
        self.x = x
        self.y = yt
        self.num_labels = len(self.mlb.classes_)
        return self


class TypeDataset(Dataset):
    def __init__(self, ent_emb, ent2id, entid2idx, x, y):
        self.ent_emb = ent_emb
        self.ent2id = ent2id
        self.entid2idx = entid2idx
        self.ents = x
        self.labels = y

    def __getitem__(self, item_idx):
        item = self.ents[item_idx]
        x_id = self.ent2id[item]
        x_idx = self.entid2idx[x_id]
        x = self.ent_emb[x_idx]
        y = np.array(item_idx)
        y = torch.FloatTensor(y)
        return x, y

    def __len__(self):
        return len(self.ents)


class TypeDataModule(pl.LightningDataModule):
    def __init__(self, x_tr, y_tr, x_val, y_val, x_test, y_test, ent_emb, ent2id, entid2idx, batch_size=16):
        super().__init__()
        self.ent_emb = ent_emb
        self.ent2id = ent2id
        self.entid2idx = entid2idx
        self.batch_size = batch_size
        self.tr_x = x_tr
        self.tr_label = y_tr
        self.val_x = x_val
        self.val_label = y_val
        self.test_x = x_test
        self.test_label = y_test

    def setup(self):
        self.train_dataset = TypeDataset(self.ent_emb, self.ent2id, self.entid2idx, self.tr_x, self.tr_label)
        self.val_dataset = TypeDataset(self.ent_emb, self.ent2id, self.entid2idx, self.val_x, self.val_label)
        self.test_dataset = TypeDataset(self.ent_emb, self.ent2id, self.entid2idx, self.test_x, self.test_label)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=2)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size)


class NodeClassifier(pl.LightningModule):
    # Set up the classifier
    def __init__(self, emb_dim=100, n_classes=50, steps_per_epoch=None, n_epochs=3, lr=2e-5):
        super().__init__()
        self.classifier = nn.Linear(emb_dim, n_classes)
        self.steps_per_epoch = steps_per_epoch
        self.n_epochs = n_epochs
        self.lr = lr
        self.criterion = nn.BCEWithLogitsLoss()

    def forward(self, ent_emb):
        output = self.classifier(ent_emb)
        return output

    def training_step(self, batch, batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('train_loss', loss, prog_bar=True, logger=True)
        return {"loss": loss, "predictions": outputs, "labels": labels}

    def validation_step(self, batch, batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('val_loss', loss, prog_bar=True, logger=True)
        return loss

    def test_step(self, batch, batch_idx):
        input_ent_emb = batch[0]
        labels = batch[1]
        outputs = self.classifier(input_ent_emb)
        loss = self.criterion(outputs, labels)
        self.log('test_loss', loss, prog_bar=True, logger=True)
        return loss

    def configure_optimizers(self):
        optimizer = Adam(self.parameters(), lr=self.lr)
        warmup_steps = self.steps_per_epoch // 3
        total_steps = self.steps_per_epoch * self.n_epochs - warmup_steps
        # scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
        # return [optimizer], [scheduler]
        return [optimizer]


RANDOM_SEED = 24


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
    # First Split for Train and Test
    x_train, x_dev, y_train, y_dev = train_test_split(x, y, test_size=0.1, random_state=RANDOM_SEED, shuffle=True)
    print(f"length train: {str(x_train)}, length dev: {str(y_dev)}")
    return x_train, x_dev, y_train, y_dev


def type_train_and_test(work_dir, train_batch_size=32, epochs=12, lr=2e-5):
    ent_emb = torch.load(f'{work_dir}ent_emb.pt', map_location='cpu')
    if isinstance(ent_emb, tuple):
        ent_emb = ent_emb[0]

    ent_emb = ent_emb.squeeze().numpy()
    num_embs, emb_dim = ent_emb.shape
    print(f'Loaded {num_embs} embeddings with dim={emb_dim}')

    emb_ids = torch.load(f'{work_dir}ents.pt', map_location='cpu')
    entid2idx = utils.make_ent2idx(emb_ids, max_ent_id=emb_ids.max()).numpy()
    maps = torch.load(f'{work_dir}maps.pt')
    ent_ids = maps['ent_ids']

    # Instantiate and set up the data_module
    data_transformer = DataTransformer(work_dir).data_transform()
    t_data_module = TypeDataModule(data_transformer.x_tr, data_transformer.y_tr,
                                   data_transformer.x_val, data_transformer.y_val,
                                   data_transformer.x_test, data_transformer.y_test,
                                   ent_emb, entid2idx, batch_size=train_batch_size)
    t_data_module.setup()

    # Instantiate the classifier model
    steps_per_epoch = len(data_transformer.x_tr) // train_batch_size
    model = NodeClassifier(n_classes=data_transformer.num_labels,
                           steps_per_epoch=steps_per_epoch,
                           n_epochs=epochs,
                           lr=lr)
    # saves a file like: input/QTag-epoch=02-val_loss=0.32.ckpt
    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',  # monitored quantity
        filename='type-{epoch:02d}-{val_loss:.2f}',
        save_top_k=2,  # save the top 2 models
        mode='min',  # mode of the monitored quantity  for optimization
    )
    # Instantiate the Model Trainer
    trainer = pl.Trainer(max_epochs=epochs, gpus=1, callbacks=[checkpoint_callback], progress_bar_refresh_rate=30)
    # Train the Classifier Model
    trainer.fit(model, t_data_module)
    # trainer.test(model, datamodule=t_data_module)
    test_dataloader = t_data_module.test_dataloader()
    return model

def pred(model, dataloader):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model.eval()
    # Tracking variables
    pred_outs, true_labels = [], []
    #i=0
    # Predict
    for batch in dataloader:
        # Add batch to GPU
        batch = tuple(t.to(device) for t in batch)
        # Unpack the inputs from our dataloader
        b_input_ids, b_attn_mask, b_labels = batch
        with torch.no_grad():
            # Forward pass, calculate logit predictions
            pred_out = model(b_input_ids,b_attn_mask)
            pred_out = torch.sigmoid(pred_out)
            # Move predicted output and labels to CPU
            pred_out = pred_out.detach().cpu().numpy()
            label_ids = b_labels.to('cpu').numpy()
        pred_outs.append(pred_out)
        true_labels.append(label_ids)
    # Combine the results across all batches.
    flat_pred_outs = np.concatenate(pred_outs, axis=0)
    # Combine the correct labels for each batch into a single list.
    flat_true_labels = np.concatenate(true_labels, axis=0)
    return flat_pred_outs, flat_true_labels


def eval_types(model, test_dataloader):
    flat_pred_outs, flat_true_labels = pred(model, test_dataloader)
    threshold = np.arange(0.4, 0.51, 0.01)
    scores = [] # Store the list of f1 scores for prediction on each threshold
    #convert labels to 1D array
    y_true = flat_true_labels.ravel()
    for thresh in threshold:
        #classes for each threshold
        pred_bin_label = classify(flat_pred_outs,thresh)
        #convert to 1D array
        y_pred = np.array(pred_bin_label).ravel()
        scores.append(metrics.f1_score(y_true,y_pred))
    # find the optimal threshold
    opt_thresh = threshold[scores.index(max(scores))]
    print(f'Optimal Threshold Value = {opt_thresh}')
    #predictions for optimal threshold
    y_pred_labels = classify(flat_pred_outs,opt_thresh)
    y_pred = np.array(y_pred_labels).ravel() # Flatten
    print(metrics.classification_report(y_true,y_pred))


def produce_types(model, data_transformer:DataTransformer, ent_emb, ent2id, entid2idx, threshold=0.4):
    produce_dataset = TypeDataset(ent_emb, ent2id, entid2idx, data_transformer.x, data_transformer.y)
    pred_sampler = SequentialSampler(produce_dataset)
    produce_dataloader = DataLoader(produce_dataset, sampler=pred_sampler, batch_size=64)
    flat_pred_outs, flat_true_labels = pred(model, produce_dataloader)
    thresh = np.float(threshold)
    #convert labels to 1D array
    y_true = flat_true_labels.ravel()
    #convert to 1D array
    y_pred_labels = classify(flat_pred_outs,thresh)
    y_pred = data_transformer.mlb.inverse_transform(np.array(y_pred_labels))
    y_act = data_transformer.mlb.inverse_transform(flat_true_labels)
    df = pd.DataFrame({'Body': data_transformer.x, 'Actual Tags': y_act, 'Predicted Tags': y_pred})
    return df


# convert probabilities into 0 or 1 based on a threshold value
def classify(pred_prob,thresh):
    y_pred = []
    for tag_label_row in pred_prob:
        temp=[]
        for tag_label in tag_label_row:
            if tag_label >= thresh:
                temp.append(1) # Infer tag value as 1 (present)
            else:
                temp.append(0) # Infer tag value as 0 (absent)
        y_pred.append(temp)
    return y_pred

# def node_classification(dataset, checkpoint):
#     ent_emb = torch.load(f'output/ent_emb-{checkpoint}.pt', map_location='cpu')
#     if isinstance(ent_emb, tuple):
#         ent_emb = ent_emb[0]
#
#     ent_emb = ent_emb.squeeze().numpy()
#     num_embs, emb_dim = ent_emb.shape
#     print(f'Loaded {num_embs} embeddings with dim={emb_dim}')
#
#     emb_ids = torch.load(f'output/ents-{checkpoint}.pt', map_location='cpu')
#     ent2idx = utils.make_ent2idx(emb_ids, max_ent_id=emb_ids.max()).numpy()
#     maps = torch.load(f'data/{dataset}/maps.pt')
#     ent_ids = maps['ent_ids']
#     class2labels = defaultdict(lambda: len(class2labels))
#
#     splits = ['train', 'dev', 'test']
#     split_2data = dict()
#     for split in splits:
#         with open(f'data/{dataset}/{split}-ents-class.txt') as f:
#             idx = []
#             labels = []
#             for line in f:
#                 entity, ent_class = line.strip().split()
#                 entity_id = ent_ids[entity]
#                 entity_idx = ent2idx[entity_id]
#                 idx.append(entity_idx)
#                 labels.append(class2labels[ent_class])
#
#             x = ent_emb[idx]
#             y = np.array(labels)
#             split_2data[split] = (x, y)
#
#     x_train, y_train = split_2data['train']
#     x_dev, y_dev = split_2data['dev']
#     x_test, y_test = split_2data['test']
#
#     best_dev_metric = 0.0
#     best_c = 0
#     for k in range(-4, 2):
#         c = 10 ** -k
#         model = LogisticRegression(C=c, multi_class='multinomial',
#                                    max_iter=1000)
#         model.fit(x_train, y_train)
#
#         dev_preds = model.predict(x_dev)
#         dev_acc = accuracy_score(y_dev, dev_preds)
#         print(f'{c:.3f} - {dev_acc:.3f}')
#
#         if dev_acc > best_dev_metric:
#             best_dev_metric = dev_acc
#             best_c = c
#
#     print(f'Best regularization coefficient: {best_c:.4f}')
#     model = LogisticRegression(C=best_c, multi_class='multinomial',
#                                max_iter=1000)
#     x_train_all = np.concatenate((x_train, x_dev))
#     y_train_all = np.concatenate((y_train, y_dev))
#     model.fit(x_train_all, y_train_all)
#
#     for metric_fn in (accuracy_score, balanced_accuracy_score):
#         train_preds = model.predict(x_train_all)
#         train_metric = metric_fn(y_train_all, train_preds)
#
#         test_preds = model.predict(x_test)
#         test_metric = metric_fn(y_test, test_preds)
#
#         print(f'Train {metric_fn.__name__}: {train_metric:.3f}')
#         print(f'Test {metric_fn.__name__}: {test_metric:.3f}')
