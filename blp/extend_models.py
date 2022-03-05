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
        self.embeddings='XX'
        if dim is None:
            dim = self.encoder.get_dim()
        super().__init__(dim, rel_model, loss_fn, num_relations, regularizer)

    def _encode_entity(self, text_tok, text_mask=None):
        if text_mask is None:
            text_mask = torch.ones_like(text_tok, dtype=torch.float)
        # Extract average of word embeddings
        embs = self.embeddings(text_tok)
        lengths = torch.sum(text_mask, dim=-1, keepdim=True)
        embs = torch.sum(text_mask.unsqueeze(dim=-1) * embs, dim=1)
        embs = embs / lengths
        return embs


class FastTextTokenizer:
    def __init__(self, uncased=True):
        self.uncased = uncased
        self.model = FastText.load(str(FASTTEXT_LOGS_MODEL))
        self.split_regex = r"[\/\-_\s,]"

    def encode(self, text, max_length, return_tensors):
        if self.uncased:
            text = text.lower()
        tokens = re.split(self.split_regex, text)
        tokens = tokens[:max_length]
        # for tok in tokens:
        #     if tok not in self.model.wv.key_to_index:
        #         self.model.build_vocab(tok, update=True)
        #         self.model.train([tokens], total_examples=1, epochs=2)
        encoded = [self.model.wv.key_to_index.get(t, self.model.wv.key_to_index['0']) for t in tokens]
        if return_tensors:
            encoded = torch.tensor(encoded)
        return encoded


