import os
import os.path as osp
from pathlib import Path
from blp.extend_models import *
from sklearn.metrics import accuracy_score, balanced_accuracy_score
import torch
import numpy as np
import utils
import pandas as pd
from collections import defaultdict
from sklearn.linear_model import LogisticRegression


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
    class2label = defaultdict(lambda: len(class2label))

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
                labels.append(class2label[ent_class])

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