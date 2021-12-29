# coding:utf-8
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import os
import time
import sys
import datetime
import ctypes
import json
import numpy as np
from sklearn.metrics import roc_auc_score
import copy
from tqdm import tqdm


class TripleProducer(object):

    def __init__(self, model = None, data_loader = None, use_gpu = True, output_file=None):
        base_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../release/Base.so"))
        self.lib = ctypes.cdll.LoadLibrary(base_file)
        self.lib.produceHead.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int64, ctypes.c_float, ctypes.c_int64]
        self.lib.produceTail.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int64, ctypes.c_float, ctypes.c_int64]
        # self.lib.test_link_prediction.argtypes = [ctypes.c_int64]

        # self.lib.getTestLinkMRR.argtypes = [ctypes.c_int64]
        # self.lib.getTestLinkMR.argtypes = [ctypes.c_int64]
        # self.lib.getTestLinkHit10.argtypes = [ctypes.c_int64]
        # self.lib.getTestLinkHit3.argtypes = [ctypes.c_int64]
        # self.lib.getTestLinkHit1.argtypes = [ctypes.c_int64]
        #
        # self.lib.getTestLinkMRR.restype = ctypes.c_float
        # self.lib.getTestLinkMR.restype = ctypes.c_float
        # self.lib.getTestLinkHit10.restype = ctypes.c_float
        # self.lib.getTestLinkHit3.restype = ctypes.c_float
        # self.lib.getTestLinkHit1.restype = ctypes.c_float

        self.model = model
        self.data_loader = data_loader
        self.use_gpu = use_gpu
        self.out_file = output_file

        if self.use_gpu:
            self.model.cuda()

    def set_model(self, model):
        self.model = model

    def set_data_loader(self, data_loader):
        self.data_loader = data_loader

    def set_use_gpu(self, use_gpu):
        self.use_gpu = use_gpu
        if self.use_gpu and self.model != None:
            self.model.cuda()

    def to_var(self, x, use_gpu):
        if use_gpu:
            return Variable(torch.from_numpy(x).cuda())
        else:
            return Variable(torch.from_numpy(x))

    def test_one_step(self, data):        
        return self.model.predict({
            'batch_h': self.to_var(data['batch_h'], self.use_gpu),
            'batch_t': self.to_var(data['batch_t'], self.use_gpu),
            'batch_r': self.to_var(data['batch_r'], self.use_gpu),
            'mode': data['mode']
        })


    def produce_triples(self, type_constrain = False, threshold=0.5):
        self.lib.initTest()
        self.data_loader.set_sampling_mode('link')
        if type_constrain:
            type_constrain = 1
        else:
            type_constrain = 0
        training_range = self.data_loader
        self.lib.setOutPath(ctypes.create_string_buffer(self.out_file.encode(), len(self.out_file) * 2))
        with tqdm(total=len(training_range), colour="green", position=0, leave=True) as pbar:
            pbar.set_description(f"TripleProducer")
            for index, [data_head, data_tail] in enumerate(training_range):
                score = self.test_one_step(data_head)
                order = np.argsort(score)
                self.lib.produceHead(score.__array_interface__["data"][0],
                                     order.__array_interface__["data"][0],
                                     index,
                                     float(threshold),
                                     type_constrain)
                score = self.test_one_step(data_tail)
                order = np.argsort(score)
                self.lib.produceTail(score.__array_interface__["data"][0],
                                     order.__array_interface__["data"][0],
                                     index,
                                     float(threshold),
                                     type_constrain)
                pbar.update(1)


