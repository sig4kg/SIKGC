from pathlib import Path
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertModel


class LinkPrediction(nn.Module):
    """A general link prediction model with a lookup table for relation
    embeddings."""
    def __init__(self, dim, rel_model, loss_fn, num_relations, regularizer):
        super().__init__()
        self.dim = dim
        self.normalize_embs = False
        self.regularizer = regularizer
        # this is used by rotate, modified by sylvia
        if rel_model == 'rotate':
            self.rel_dim = int(self.dim / 2)
        else:
            self.rel_dim = self.dim
        self.rel_emb = nn.Embedding(num_relations, self.rel_dim)
        self.embedding_range = calculate_rel_embedding_range(self.rel_emb.weight.data)
        nn.init.xavier_uniform_(self.rel_emb.weight.data)

        if rel_model == 'transe':
            self.score_fn = transe_score
            self.normalize_embs = True
        elif rel_model == 'distmult':
            self.score_fn = distmult_score
        elif rel_model == 'complex':
            self.score_fn = complex_score
        elif rel_model == 'simple':
            self.score_fn = simple_score
        elif rel_model == 'rotate':
            self.score_fn = lambda heads, tails, rels: rotate_score(heads, tails, rels, self.embedding_range)
        else:
            raise ValueError(f'Unknown relational model {rel_model}.')

        if loss_fn == 'margin':
            self.loss_fn = margin_loss
        elif loss_fn == 'nll':
            self.loss_fn = nll_loss
        elif loss_fn == 'sigmoid':
            self.loss_fn = sigmoid_loss
        else:
            raise ValueError(f'Unkown loss function {loss_fn}')

    def encode(self, *args, **kwargs):
        ent_emb = self._encode_entity(*args, **kwargs)
        if self.normalize_embs:
            ent_emb = F.normalize(ent_emb, dim=-1)

        return ent_emb

    def _encode_entity(self, *args, **kwargs):
        raise NotImplementedError

    def forward(self, *args, **kwargs):
        raise NotImplementedError

    def compute_loss(self, ent_embs, rels, neg_idx):
        batch_size = ent_embs.shape[0]

        # Scores for positive samples
        try:
            rels = self.rel_emb(rels)
        except Exception:
            print("stop")
        heads, tails = torch.chunk(ent_embs, chunks=2, dim=1)
        pos_scores = self.score_fn(heads, tails, rels)

        if self.regularizer > 0:
            reg_loss = self.regularizer * l2_regularization(heads, tails, rels)
        else:
            reg_loss = 0

        # Scores for negative samples
        neg_embs = ent_embs.view(batch_size * 2, -1)[neg_idx]
        heads, tails = torch.chunk(neg_embs, chunks=2, dim=2)
        neg_scores = self.score_fn(heads.squeeze(), tails.squeeze(), rels)
        model_loss = self.loss_fn(pos_scores, neg_scores)
        return model_loss + reg_loss


# modified by Sylvia Wang
def calculate_rel_embedding_range(tensor):
    dimensions = tensor.dim()
    if dimensions < 2:
        raise ValueError("Fan in and fan out can not be computed for tensor with fewer than 2 dimensions")

    num_input_fmaps = tensor.size(1)
    num_output_fmaps = tensor.size(0)
    receptive_field_size = 1
    if tensor.dim() > 2:
        receptive_field_size = tensor[0][0].numel()
    fan_in = num_input_fmaps * receptive_field_size
    fan_out = num_output_fmaps * receptive_field_size
    std = math.sqrt(2.0 / float(fan_in + fan_out))
    a = math.sqrt(3.0) * std
    embedding_range = nn.Parameter(
        torch.Tensor([a]),
        requires_grad=False
    )
    return embedding_range


class InductiveLinkPrediction(LinkPrediction):
    """Description-based Link Prediction (DLP)."""
    def _encode_entity(self, text_tok, text_mask):
        raise NotImplementedError

    def forward(self, text_tok, text_mask, rels=None, neg_idx=None):
        batch_size, _, num_text_tokens = text_tok.shape

        # Encode text into an entity representation from its description
        ent_embs = self.encode(text_tok.view(-1, num_text_tokens),
                               text_mask.view(-1, num_text_tokens))

        if rels is None and neg_idx is None:
            # Forward is being used to compute entity embeddings only
            out = ent_embs
        else:
            # Forward is being used to compute link prediction loss
            ent_embs = ent_embs.view(batch_size, 2, -1)
            out = self.compute_loss(ent_embs, rels, neg_idx)

        return out


class BertEmbeddingsLP(InductiveLinkPrediction):
    """BERT for Link Prediction (BLP)."""
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
        self.enc_linear = nn.Linear(hidden_size, self.dim, bias=False)

    def _encode_entity(self, text_tok, text_mask):
        # Extract BERT representation of [CLS] token
        embs = self.encoder(text_tok, text_mask)[0][:, 0]
        embs = self.enc_linear(embs)
        return embs


class WordEmbeddingsLP(InductiveLinkPrediction):
    """Description encoder with pretrained embeddings, obtained from BERT or a
    specified tensor file.
    """
    def __init__(self, rel_model, loss_fn, num_relations, regularizer,
                 dim=None, encoder_name=None, embeddings=None):
        if not encoder_name and not embeddings:
            raise ValueError('Must provided one of encoder_name or embeddings')

        if encoder_name is not None:
            bert_path = "../saved_models/bert-base-cased"
            local_models = Path(bert_path)
            if local_models.exists():
                encoder = BertModel.from_pretrained(bert_path)
            else:
                encoder = BertModel.from_pretrained(encoder_name)
            embeddings = encoder.embeddings.word_embeddings
        else:
            emb_tensor = torch.load(embeddings)
            num_embeddings, embedding_dim = emb_tensor.shape
            embeddings = nn.Embedding(num_embeddings, embedding_dim)
            embeddings.weight.data = emb_tensor

        if dim is None:
            dim = embeddings.embedding_dim

        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)

        self.embeddings = embeddings

    def _encode_entity(self, text_tok, text_mask):
        raise NotImplementedError


class BOW(WordEmbeddingsLP):
    """Bag-of-words (BOW) description encoder, with BERT low-level embeddings.
    """
    def _encode_entity(self, text_tok, text_mask=None):
        if text_mask is None:
            text_mask = torch.ones_like(text_tok, dtype=torch.float)
        # Extract average of word embeddings
        embs = self.embeddings(text_tok)
        lengths = torch.sum(text_mask, dim=-1, keepdim=True)
        embs = torch.sum(text_mask.unsqueeze(dim=-1) * embs, dim=1)
        embs = embs / lengths
        return embs


class DKRL(WordEmbeddingsLP):
    """Description-Embodied Knowledge Representation Learning (DKRL) with CNN
    encoder, after
    Zuo, Yukun, et al. "Representation learning of knowledge graphs with
    entity attributes and multimedia descriptions."
    """

    def __init__(self, dim, rel_model, loss_fn, num_relations, regularizer,
                 encoder_name=None, embeddings=None):
        super().__init__(rel_model, loss_fn, num_relations, regularizer,
                         dim, encoder_name, embeddings)

        emb_dim = self.embeddings.embedding_dim
        self.conv1 = nn.Conv1d(emb_dim, self.dim, kernel_size=2)
        self.conv2 = nn.Conv1d(self.dim, self.dim, kernel_size=2)

    def _encode_entity(self, text_tok, text_mask):
        if text_mask is None:
            text_mask = torch.ones_like(text_tok, dtype=torch.float)
        # Extract word embeddings and mask padding
        embs = self.embeddings(text_tok) * text_mask.unsqueeze(dim=-1)

        # Reshape to (N, C, L)
        embs = embs.transpose(1, 2)
        text_mask = text_mask.unsqueeze(1)

        # Pass through CNN, adding padding for valid convolutions
        # and masking outputs due to padding
        embs = F.pad(embs, [0, 1])
        embs = self.conv1(embs)
        embs = embs * text_mask
        if embs.shape[2] >= 4:
            kernel_size = 4
        elif embs.shape[2] == 1:
            kernel_size = 1
        else:
            kernel_size = 2
        embs = F.max_pool1d(embs, kernel_size=kernel_size)
        text_mask = F.max_pool1d(text_mask, kernel_size=kernel_size)
        embs = torch.tanh(embs)
        embs = F.pad(embs, [0, 1])
        embs = self.conv2(embs)
        lengths = torch.sum(text_mask, dim=-1)
        embs = torch.sum(embs * text_mask, dim=-1) / lengths
        embs = torch.tanh(embs)

        return embs


class TransductiveLinkPrediction(LinkPrediction):
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


def transe_score(heads, tails, rels):
    return -torch.norm(heads + rels - tails, dim=-1, p=1)


def distmult_score(heads, tails, rels):
    return torch.sum(heads * rels * tails, dim=-1)


def complex_score(heads, tails, rels):
    heads_re, heads_im = torch.chunk(heads, chunks=2, dim=-1)
    tails_re, tails_im = torch.chunk(tails, chunks=2, dim=-1)
    rels_re, rels_im = torch.chunk(rels, chunks=2, dim=-1)

    return torch.sum(rels_re * heads_re * tails_re +
                     rels_re * heads_im * tails_im +
                     rels_im * heads_re * tails_im -
                     rels_im * heads_im * tails_re,
                     dim=-1)


def simple_score(heads, tails, rels):
    heads_h, heads_t = torch.chunk(heads, chunks=2, dim=-1)
    tails_h, tails_t = torch.chunk(tails, chunks=2, dim=-1)
    rel_a, rel_b = torch.chunk(rels, chunks=2, dim=-1)

    return torch.sum(heads_h * rel_a * tails_t +
                     tails_h * rel_b * heads_t, dim=-1) / 2


def rotate_score(heads, tails, rels, embedding_range):
    pi = 3.14159265358979323846
    re_head, im_head = torch.chunk(heads, chunks=2, dim=-1)
    re_tail, im_tail = torch.chunk(tails, chunks=2, dim=-1)
    # re_relation, im_relation = torch.chunk(rels, chunks=2, dim=-1)
    phase_relation = rels / (embedding_range / pi)
    re_relation = torch.cos(phase_relation)
    im_relation = torch.sin(phase_relation)
    re_score = re_head * re_relation - im_head * im_relation
    im_score = re_head * im_relation + im_head * re_relation
    re_score = re_score - re_tail
    im_score = im_score - im_tail
    score = torch.stack([re_score, im_score], dim=0)
    score = score.norm(dim=0)
    score = -score.sum(dim=-1)
    return score



def margin_loss(pos_scores, neg_scores):
    loss = 1 - pos_scores + neg_scores
    loss[loss < 0] = 0
    return loss.mean()


def nll_loss(pos_scores, neg_scores):
    return (F.softplus(-pos_scores).mean() + F.softplus(neg_scores).mean()) / 2


def sigmoid_loss(pos_scores, neg_scores):
    negative_score = F.logsigmoid(-neg_scores).mean(dim = 1)
    positive_score = F.logsigmoid(pos_scores).squeeze(dim = 1)
    positive_sample_loss = - positive_score.mean()
    negative_sample_loss = - negative_score.mean()
    loss = (positive_sample_loss + negative_sample_loss)/2
    return loss


def l2_regularization(heads, tails, rels):
    reg_loss = 0.0
    for tensor in (heads, tails, rels):
        reg_loss += torch.mean(tensor ** 2)

    return reg_loss / 3.0
