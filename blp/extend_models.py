import numpy as np

from models import *
from gensim.models.fasttext import FastText
import re
import torch
import torch.nn as nn


# Sylvia  Wang for TREAT test
FASTTEXT_LOGS_MODEL = "../saved_models/fasttext_entity/entity_fx_log"


class FastTextEmbeddingLP(InductiveLinkPrediction):
    """FastText for Link Prediction."""
    def __init__(self, dim, rel_model, loss_fn, num_relations,
                 regularizer):
        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)
        self.encoder = FastText.load(str(FASTTEXT_LOGS_MODEL))
        hidden_size = self.encoder.vector_size
        self.enc_linear = nn.Linear(hidden_size, self.dim, bias=False)

    def _encode_entity(self, text_tok, text_mask=None):
        # manually norm the embedding, this also works. --Sylvia
        # embs = torch.tensor(self.encoder.wv.vectors[text_tok])
        # norm_values = torch.norm(embs, p=2, dim=2, keepdim=True)
        # divide_norm = torch.where(norm_values > 0, torch.divide(embs, norm_values), embs)
        # embs = torch.mean(divide_norm, dim=1)
        #  fasttext provide normed vectors, to same computing time, we use the normed vector directly from model
        # average
        emnorm = torch.tensor(self.encoder.wv.get_normed_vectors()[text_tok])
        embs = torch.mean(emnorm, dim=1)
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


def test_fasttext():
    tk = FastTextTokenizer()
    t1 = tk.model.wv.similarity("NFS amf_09", "NF am_08")
    en1 = tk.encode("NFS amf 09", 4, True)
    en2 = tk.encode("NF am 08", 4, True)
    em1 = torch.tensor(tk.model.wv.vectors[en1])
    em2 = torch.tensor(tk.model.wv.vectors[en2])
    norm_values1 = torch.norm(em1, p=2, dim=2, keepdim=True)
    divide_norm1 = torch.where(norm_values1 > 0, torch.divide(em1, norm_values1), em1)
    em1 = torch.mean(divide_norm1, dim=1)
    norm_values2 = torch.norm(em2, p=2, dim=2, keepdim=True)
    divide_norm2 = torch.where(norm_values2 > 0, torch.divide(em2, norm_values2), em2)
    em2 = torch.mean(divide_norm2, dim=1)
    t2 = torch.cosine_similarity(em1, em2)
    emnorm1 = torch.tensor(tk.model.wv.get_normed_vectors()[en1])
    emnorm2 = torch.tensor(tk.model.wv.get_normed_vectors()[en2])
    emmean1 = torch.mean(emnorm1, dim=1)
    emmean2 = torch.mean(emnorm2, dim=1)
    t3 = torch.cosine_similarity(emmean1, emmean2)
    print(t1)
    print(t2)
    print(t3)



class RotateLinkPrediction(LinkPrediction):
    def __init__(self, dim, rel_model, loss_fn, num_entities, num_relations,
                 regularizer):
        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)
        self.ent_emb = nn.Embedding(num_entities, dim)
        nn.init.xavier_uniform_(self.ent_emb.weight.data)

    def _encode_entity(self, entities):
        return self.ent_emb(entities)

    def forward(self, pos_pairs, rels, neg_idx):
        embs = self.encode(pos_pairs)
        return self.compute_loss(embs, rels, neg_idx)


class RotateBertEmbeddingsLP(InductiveLinkPrediction):
    """Rotate BERT for Link Prediction (BLP)."""
    def __init__(self, dim, rel_model, loss_fn, num_relations, encoder_name,
                 regularizer):
        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)

        bert_path = "../saved_models/bert-base-cased"
        local_models = Path(bert_path)
        if local_models.exists():
            self.encoder = BertModel.from_pretrained(bert_path,
                                                     output_attentions=False,
                                                     output_hidden_states=False)
        else:
            self.encoder = BertModel.from_pretrained(encoder_name,
                                                     output_attentions=False,
                                                     output_hidden_states=False)
        hidden_size = self.encoder.config.hidden_size
        self.enc_linear = nn.Linear(hidden_size, self.dim * 2, bias=False)

    def _encode_entity(self, text_tok, text_mask):
        # Extract BERT representation of [CLS] token
        embs = self.encoder(text_tok, text_mask)[0][:, 0]
        embs = self.enc_linear(embs)
        return embs


if __name__ == '__main__':
    test_fasttext()




