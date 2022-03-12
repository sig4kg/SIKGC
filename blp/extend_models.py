import numpy as np

from models import *
from gensim.models.fasttext import FastText
import re


# Sylvia  Wang for TREAT test
FASTTEXT_LOGS_MODEL = "../saved_models/fasttext_logs/fx_log"


class FastTextEmbeddingLP(InductiveLinkPrediction):
    """FastText for Link Prediction."""
    def __init__(self, dim, rel_model, loss_fn, num_relations,
                 regularizer):
        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)
        self.encoder = FastText.load(str(FASTTEXT_LOGS_MODEL))
        hidden_size = self.encoder.vector_size
        self.enc_linear = nn.Linear(hidden_size, self.dim, bias=False)

    def _encode_entity(self, text_tok, text_mask=None):
        embs = torch.tensor(self.encoder.wv.vectors[text_tok])
        norm_values = torch.norm(embs, p=2, dim=2, keepdim=True)
        divide_norm = torch.where(norm_values > 0, torch.divide(embs, norm_values), embs)
        # average
        embs = torch.mean(divide_norm, dim=1)
        embs = self.enc_linear(embs)
        return embs


class FastTextTokenizer:
    def __init__(self, uncased=True):
        self.uncased = uncased
        self.model = FastText.load(str(FASTTEXT_LOGS_MODEL))
        self.split_regex = r"[\-_\s,]"

    def encode(self, text, max_length, return_tensors):
        if self.uncased:
            text = text.lower()
        tokens = re.split(self.split_regex, text)
        tokens = tokens[:max_length]
        encoded = [self.model.wv.key_to_index.get(t, self.model.wv.key_to_index['0']) for t in tokens]
        if return_tensors:
            encoded = torch.tensor([encoded])
        return encoded


