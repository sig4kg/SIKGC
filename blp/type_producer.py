from torch.utils.data import DataLoader, Dataset, SequentialSampler
from torch.optim import Adam
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources
from blp.extend_models import *
import torch
import numpy as np
import utils
import pandas as pd
from collections import Counter
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from sklearn import metrics


###
# Author: Sylvia Wang
# 2022/05
###
from file_util import save_to_file


class DataTransformer():
    def __init__(self):
        self.data_dir = ""
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

    def data_transform_read_file(self, data_dir):
        self.data_dir = data_dir
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

    def data_transform_from_context(self, context_resource: ContextResources, work_dir, num_classes=50):
        self.data_dir = work_dir
        x = []
        y = []
        x_train, x_dev, x_test, y_train, y_dev, y_test = split_data(context_resource, work_dir, num=num_classes)
        y.extend(y_train)
        y.extend(y_dev)
        y.extend(y_test)
        x.extend(x_train)
        x.extend(x_dev)
        x.extend(x_test)
        yt = self.mlb.fit_transform(y)
        print("node classification sample data: ")
        # Getting a sense of how the tags data looks like
        print(yt[0])
        print(self.mlb.inverse_transform(yt[0].reshape(1, -1)))
        print(self.mlb.classes_)
        self.x_tr = x_train
        self.y_tr = yt[:len(x_train)]
        self.x_val = x_dev
        self.y_val = yt[len(x_train): len(x_train) + len(x_dev)]
        self.x_test = x_test
        self.y_test = yt[len(x_train) + len(x_dev):]
        self.x = x
        self.y = yt
        self.num_labels = len(self.mlb.classes_)
        return self


class TypeDataset(Dataset):
    def __init__(self, context_id2ent, ent_emb, ent2id, entid2idx, x, y):
        self.context_id2ent = context_id2ent
        self.ent_emb = ent_emb
        self.ent2id = ent2id
        self.entid2idx = entid2idx
        self.ents = x
        self.labels = y
        self.size = len(x)

    def __getitem__(self, item_idx):
        context_id = self.ents[item_idx]
        ent_str = self.context_id2ent[context_id]
        x_id = self.ent2id[ent_str]
        x_idx = self.entid2idx[x_id]
        x = self.ent_emb[x_idx]
        y = torch.tensor(self.labels[item_idx], dtype=torch.float)
        return x, y

    def __len__(self):
        return len(self.ents)


class TypeDataModule(pl.LightningDataModule):
    def __init__(self, x_tr, y_tr, x_val, y_val, x_test, y_test, context_id2ent, ent_emb, ent2id, entid2idx,
                 batch_size=16):
        super().__init__()
        self.context_id2ent = context_id2ent
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

    def setup(self, stage=None):
        self.train_dataset = TypeDataset(self.context_id2ent, self.ent_emb, self.ent2id, self.entid2idx, self.tr_x,
                                         self.tr_label)
        self.val_dataset = TypeDataset(self.context_id2ent, self.ent_emb, self.ent2id, self.entid2idx, self.val_x,
                                       self.val_label)
        self.test_dataset = TypeDataset(self.context_id2ent, self.ent_emb, self.ent2id, self.entid2idx, self.test_x,
                                        self.test_label)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=2)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size)


class NodeClassifier(pl.LightningModule):
    # Set up the classifier
    def __init__(self, emb_dim=128, n_classes=50, steps_per_epoch=None, n_epochs=3, lr=2e-5):
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
        outputs = self(input_ent_emb)
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


class EmbeddingUtil():
    def __init__(self, work_dir):
        ent_emb = torch.load(f'{work_dir}ent_emb.pt', map_location='cpu')
        if isinstance(ent_emb, tuple):
            ent_emb = ent_emb[0]

        self.ent_emb = ent_emb.squeeze().numpy()
        num_embs, emb_dim = self.ent_emb.shape
        print(f'Loaded {num_embs} embeddings with dim={emb_dim}')
        emb_ids = torch.load(f'{work_dir}ents.pt', map_location='cpu')
        self.entid2idx = utils.make_ent2idx(emb_ids, max_ent_id=emb_ids.max()).numpy()
        maps = torch.load(f'{work_dir}maps.pt')
        self.ent_ids = maps['ent_ids']


def split_data(context_resource: ContextResources, work_dir, num=50, save_file=False):
    all_classes = [i for cls in context_resource.entid2classids.values() for i in cls]
    top_n = Counter(all_classes).most_common(num)
    top_n_tags = [i[0] for i in top_n]
    all_ents = pd.concat([context_resource.hrt_int_df['head'], context_resource.hrt_int_df['tail']],
                         axis=0).drop_duplicates(keep='first')
    all_ents = all_ents.values.tolist()
    x = []
    y = []
    for i in context_resource.entid2classids:
        if i not in all_ents:
            continue
        temp = []
        for t in context_resource.entid2classids[i]:
            if t in top_n_tags:
                temp.append(t)
        if len(temp) > 0:
            x.append(i)
            y.append(temp)
    # First Split for Train and Test
    x_train, x_dev, y_train, y_dev = train_test_split(x, y, test_size=0.1, random_state=24, shuffle=True)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=24, shuffle=True)
    print(f"length train: {str(len(x_train))}, length dev: {str(len(y_dev))}")
    if save_file:
        write_xy_to_file(x_train, y_train, work_dir + "type_train.txt")
        write_xy_to_file(x_dev, y_dev, work_dir + "type_dev.txt")
        write_xy_to_file(x_test, y_test, work_dir + "type_test.txt")
    return x_train, x_dev, x_test, y_train, y_dev, y_test


def write_xy_to_file(x, y, context_resource: ContextResources, file_name):
    content = ""
    for i in range(len(x)):
        content = content + f"{context_resource.id2ent[x[i]]}\t" + "\t".join(
            context_resource.classid2class[y[i]]) + "\n"
    with open(file_name, mode='w') as f:
        f.write(content)


def train(data_transformer: DataTransformer, t_data_module: TypeDataModule, train_batch_size=32, epochs=12, lr=2e-5):
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
    trainer = pl.Trainer(max_epochs=epochs, gpus=[], callbacks=[checkpoint_callback], progress_bar_refresh_rate=30)
    # Train the Classifier Model
    trainer.fit(model, t_data_module)
    # trainer.test(model, datamodule=t_data_module)
    test_dataloader = t_data_module.test_dataloader()
    log_file_name = data_transformer.data_dir + "blp_eval.log"
    opt_thresh = eval_types(model, test_dataloader, log_file_name)
    return model, opt_thresh


def pred(model, dataloader):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model.eval()
    # Tracking variables
    pred_outs, true_labels = [], []
    # i=0
    # Predict
    for batch in dataloader:
        # Add batch to GPU
        batch = tuple(t.to(device) for t in batch)
        # Unpack the inputs from our dataloader
        b_input_ids, b_labels = batch
        with torch.no_grad():
            # Forward pass, calculate logit predictions
            pred_out = model(b_input_ids)
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


def eval_types(model, test_dataloader, log_file):
    flat_pred_outs, flat_true_labels = pred(model, test_dataloader)
    threshold = np.arange(0.4, 0.51, 0.01)
    scores = []  # Store the list of f1 scores for prediction on each threshold
    # convert labels to 1D array
    y_true = flat_true_labels.ravel()
    for thresh in threshold:
        # classes for each threshold
        pred_bin_label = classify(flat_pred_outs, thresh)
        # convert to 1D array
        y_pred = np.array(pred_bin_label).ravel()
        scores.append(metrics.f1_score(y_true, y_pred))
    # find the optimal threshold
    opt_thresh = threshold[scores.index(max(scores))]
    log_str = "-------blp type prediction eval---------\n" + \
              f'Type prediction: Optimal Threshold Value = {opt_thresh}\n'
    print(log_str)
    save_to_file(log_str, log_file, mode='a')
    # predictions for optimal threshold
    y_pred_labels = classify(flat_pred_outs, opt_thresh)
    y_pred = np.array(y_pred_labels).ravel()  # Flatten
    print(metrics.classification_report(y_true, y_pred))
    save_to_file(str(metrics.classification_report(y_true, y_pred)) + "\n", log_file, mode='a')
    return opt_thresh


def produce_types(model, context_resource: ContextResources, data_transformer: DataTransformer, emb_util: EmbeddingUtil,
                  threshold=0.4):
    produce_dataset = TypeDataset(context_id2ent=context_resource.id2ent,
                                  ent_emb=emb_util.ent_emb,
                                  ent2id=emb_util.ent_ids,
                                  entid2idx=emb_util.entid2idx,
                                  x=data_transformer.x,
                                  y=data_transformer.y)
    pred_sampler = SequentialSampler(produce_dataset)
    produce_dataloader = DataLoader(produce_dataset, sampler=pred_sampler, batch_size=64)
    flat_pred_outs, flat_true_labels = pred(model, produce_dataloader)
    thresh = float(threshold)
    # convert to 1D array
    y_pred_labels = classify(flat_pred_outs, thresh)
    y_pred = data_transformer.mlb.inverse_transform(np.array(y_pred_labels))
    # y_act = data_transformer.mlb.inverse_transform(flat_true_labels)
    df = pd.DataFrame({'head': data_transformer.x, 'pred': y_pred})

    def explode(tmp_df, col, rename_col):
        tmp_df[col] = tmp_df[col].apply(lambda x: list(x))
        return tmp_df.drop(col, axis=1).join(
            pd.DataFrame(list(tmp_df[col])).stack().reset_index(drop=True).rename(rename_col)
        )
    df = explode(df, 'pred', 'tail')
    df['rel'] = 0
    df = df[['head', 'rel', 'tail']].astype('int64')
    return df


# convert probabilities into 0 or 1 based on a threshold value
def classify(pred_prob, thresh):
    y_pred = []
    for tag_label_row in pred_prob:
        temp = []
        for tag_label in tag_label_row:
            if tag_label >= thresh:
                temp.append(1)  # Infer tag value as 1 (present)
            else:
                temp.append(0)  # Infer tag value as 0 (absent)
        y_pred.append(temp)
    return y_pred


def train_and_produce(work_dir, context_resource: ContextResources, train_batch_size=32, epochs=80, lr=2e-4,
                      num_classes=50):
    emb_util = EmbeddingUtil(work_dir)
    data_transformer = DataTransformer().data_transform_from_context(context_resource, work_dir=work_dir,
                                                                     num_classes=num_classes)
    # Instantiate and set up the data_module
    t_data_module = TypeDataModule(data_transformer.x_tr, data_transformer.y_tr,
                                   data_transformer.x_val, data_transformer.y_val,
                                   data_transformer.x_test, data_transformer.y_test,
                                   context_resource.id2ent, emb_util.ent_emb, emb_util.ent_ids, emb_util.entid2idx,
                                   batch_size=train_batch_size)
    model, opt_thresh = train(data_transformer=data_transformer, t_data_module=t_data_module,
                              train_batch_size=train_batch_size, epochs=epochs, lr=lr)
    df = produce_types(model=model,
                       context_resource=context_resource,
                       emb_util=emb_util,
                       data_transformer=data_transformer,
                       threshold=opt_thresh)
    return df


def type_eval(work_dir, context_resource: ContextResources, train_batch_size=32, epochs=12, lr=2e-5, num_classes=50,
              from_file=False):
    emb_util = EmbeddingUtil(work_dir)
    if from_file:
        data_transformer = DataTransformer().data_transform_read_file(work_dir)
    else:
        data_transformer = DataTransformer().data_transform_from_context(context_resource,
                                                                         work_dir=work_dir,
                                                                         num_classes=num_classes)
    # Instantiate and set up the data_module
    t_data_module = TypeDataModule(data_transformer.x_tr, data_transformer.y_tr,
                                   data_transformer.x_val, data_transformer.y_val,
                                   data_transformer.x_test, data_transformer.y_test,
                                   context_resource.id2ent, emb_util.ent_emb, emb_util.ent_ids, emb_util.entid2idx,
                                   batch_size=train_batch_size)
    model, opt_thresh = train(data_transformer=data_transformer, t_data_module=t_data_module,
                              train_batch_size=train_batch_size, epochs=epochs, lr=lr)
    return model, opt_thresh


if __name__ == "__main__":
    folder = "../outputs/test/"
    abox_file_path = folder + "abox_hrt_uri.txt"
    context_resource = ContextResources(abox_file_path, class_and_op_file_path=folder,
                                        work_dir=folder)
    abox_scanner_scheduler = AboxScannerScheduler("../resources/TREAT/tbox_patterns/", context_resource)
    val, inv = abox_scanner_scheduler.register_patterns_all().scan_rel_IJPs(work_dir=folder)
    context_resource.hrt_int_df = val
    train_and_produce(folder + "L/", context_resource=context_resource, epochs=2)
