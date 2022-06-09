import copy
import random

import pandas as pd
import numpy as np
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources
from blp.data import *
from pipelines.exp_config import DatasetConfig


def get_maps_context2blpid(context_resource: ContextResources, blp_ent2id, blp_rel2id):
    # get context_id to blp_id
    # get blp_id to context_id
    context2blp_entid = {context_resource.ent2id[c_ent]: blp_ent2id[c_ent] for c_ent in context_resource.ent2id
                         if c_ent in context_resource.ent2id and c_ent in blp_ent2id}
    context2blp_relid = {context_resource.op2id[c_rel]: blp_rel2id[c_rel] for c_rel in context_resource.op2id
                         if c_rel in context_resource.op2id and c_rel in blp_rel2id}
    blp2context_entid = {context2blp_entid[key]: key for key in context2blp_entid}
    blp2context_relid = {context2blp_relid[key]: key for key in context2blp_relid}
    return context2blp_entid, blp2context_entid, context2blp_relid, blp2context_relid


class NegSampler:
    def __init__(self, context_resource: ContextResources,
                 abox_scanner_scheduler: AboxScannerScheduler,
                 blp_ent2id, blp_rel2id):
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.blp_ent2id = blp_ent2id
        self.context2blp_entid, self.blp2context_entid, self.context2blp_relid, self.blp2context_relid = \
            get_maps_context2blpid(context_resource, blp_ent2id, blp_rel2id)

    def reasoning_for_neg_in_batch_entities(self, data_list,
                                            batch_entities, i_rh2tid, i_rt2hid):
        # data_list are in URI, we need convert URI to context_resource ids
        candidate_ents_contextid = [self.blp2context_entid[e] for e in torch.unique(batch_entities).tolist()]
        pos_hrt_int = []
        for row_idx, row in enumerate(data_list):
            h, t, r = row[0].item(), row[1].item(), row[2].item()
            pos_hrt_int.append([self.blp2context_entid[h], self.blp2context_relid[r], self.blp2context_entid[t]])
        pos_examples_df = pd.DataFrame(data=pos_hrt_int, columns=['head', 'rel', 'tail'])
        corrupt = pd.DataFrame()
        corrupt['c_h'] = pos_examples_df['head'].apply(func=lambda x: random.sample(candidate_ents_contextid, 8))
        corrupt['rel'] = pos_examples_df['rel']
        corrupt['c_t'] = pos_examples_df['tail'].apply(func=lambda x: random.sample(candidate_ents_contextid, 8))
        corrupt.reset_index(drop=True)

        def explode(tmp_df, col, rename_col) -> pd.DataFrame:
            tmp_df[col] = tmp_df[col].apply(lambda x: list(x))
            tm = pd.DataFrame(list(tmp_df[col])).stack().reset_index(level=0)
            tm = tm.rename(columns={0: rename_col}).join(tmp_df, on='level_0'). \
                drop(axis=1, labels=[col, 'level_0']).reset_index(drop=True)
            return tm

        corrupt = explode(corrupt, "c_h", "head").dropna(how='any')
        corrupt = explode(corrupt, "c_t", "tail")
        corrupt = corrupt[['head', 'rel', 'tail']].dropna(how='any').astype('int64')
        to_scan_df = pd.concat([pos_examples_df, corrupt]).drop_duplicates(keep="first").reset_index(
            drop=True)
        self.context_resource.hrt_to_scan_df = to_scan_df
        self.context_resource.hrt_int_df = pos_examples_df
        _, inv = self.abox_scanner_scheduler.scan_rel_IJPs(work_dir="", save_result=False, log_process=False)
        # to blp ids
        inv_blp_df = inv[['head', 'tail', 'rel']]
        inv_blp_df['head'] = inv_blp_df['head'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        inv_blp_df['tail'] = inv_blp_df['tail'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        inv_blp_df['rel'] = inv_blp_df['rel'].apply(
            lambda x: self.context2blp_relid[x] if x in self.context2blp_relid else np.nan)
        inv_blp_df = inv_blp_df.dropna(how='any').astype('int64')
        return list_to_dict(inv_blp_df.to_numpy().tolist(), i_rh2tid, i_rt2hid)


def get_schema_aware_neg_sampling_indices(data_list,
                                          batch_entities,
                                          rh2t, rt2h,
                                          i_rh2tid, i_rt2hid,
                                          batch_size,
                                          num_negatives,
                                          repeats=1,
                                          schema_aware=False):
    batch_entities_np = batch_entities.numpy()
    num_ents = batch_size * 2
    idx = torch.arange(num_ents).reshape(batch_size, 2)  # n rows, 2 columns
    half_neg_num = int(num_negatives / 2)
    # for each row, generate half_neg_num head neg samples and  half_neg_num tail neg samples
    # sample head
    # fill with inconsistent triples first, then fill the left with random entities
    # For each row, sample entities, assigning 0 probability to entities
    # of the same row
    tail_weights = []
    head_weights = []
    for row_idx, row in enumerate(data_list):
        # corrupt tail, sampling weight for each entity in batch
        row_tail_weights = torch.ones(num_ents, dtype=torch.float)
        # corrupt head,  sampling weight for each entity in batch
        row_head_weights = torch.ones(num_ents, dtype=torch.float)
        # row_zeros = torch.zeros(2)  # same dim as idx, per row
        # row_ent_idx = idx[row_idx]
        # row_tail_weights.scatter_(0, row_ent_idx, row_zeros)
        h, t, r = row[0].item(), row[1].item(), row[2].item()
        # corrupt tail
        # exclude pos triples
        if r in rh2t:
            rh = rh2t[r]
            if h in rh:
                pos_t = rh[h]
                pos_t_ent_idx = [key for key, val in enumerate(batch_entities_np) if val in pos_t]
                pos_t_ent_idx = torch.tensor(pos_t_ent_idx, dtype=torch.int64)
                row_t_zeros_pos = torch.full(pos_t_ent_idx.shape, fill_value=0.0)
                row_tail_weights.scatter_(0, pos_t_ent_idx, row_t_zeros_pos)
        if r in rt2h:
            rt = rt2h[r]
            if t in rt:
                pos_h = rt[t]
                pos_h_ent_idx = [key for key, val in enumerate(batch_entities_np) if val in pos_h]
                pos_h_ent_idx = torch.tensor(pos_h_ent_idx, dtype=torch.int64)
                row_h_zeros_pos = torch.full(pos_h_ent_idx.shape, fill_value=0.0)
                row_head_weights.scatter_(0, pos_h_ent_idx, row_h_zeros_pos)
        # set higher weight for inconsistent triples
        if schema_aware:
            if r in i_rh2tid:
                i_rh = i_rh2tid[r]
                if h in i_rh:
                    possible_neg_t = i_rh[h]
                    inco_t_ent_idx = [key for key, val in enumerate(batch_entities_np) if val in possible_neg_t]
                    inco_t_ent_idx = torch.tensor(inco_t_ent_idx, dtype=torch.int64)
                    row_t_twos = torch.full(inco_t_ent_idx.shape, fill_value=10.0)
                    row_tail_weights.scatter_(0, inco_t_ent_idx, row_t_twos)
            if r in i_rt2hid:
                i_rt = i_rt2hid[r]
                if t in i_rt:
                    possible_neg_h = i_rt[t]
                    inco_h_ent_idx = [key for key, val in enumerate(batch_entities_np) if val in possible_neg_h]
                    inco_h_ent_idx = torch.tensor(inco_h_ent_idx, dtype=torch.int64)
                    row_h_twos = torch.full(inco_h_ent_idx.shape, fill_value=10.0)
                    row_head_weights.scatter_(0, inco_h_ent_idx, row_h_twos)
        tail_weights.append(row_tail_weights)
        head_weights.append(row_head_weights)

    # sampling  tail
    tail_weights = torch.stack(tail_weights)
    random_t_idx = tail_weights.multinomial(half_neg_num * repeats,
                                            replacement=True)
    random_t_idx = random_t_idx.t().flatten()
    # corrupt the second column
    tail_batch_row_selector = torch.arange(batch_size * half_neg_num * repeats)
    tail_batch_col_selector = torch.ones(batch_size * half_neg_num * repeats, dtype=torch.long)  # corrupt tail
    # Fill the array of negative samples with the sampled random entities
    # at the tail positions
    neg_t_idx = idx.repeat((half_neg_num * repeats, 1))
    neg_t_idx[tail_batch_row_selector, tail_batch_col_selector] = random_t_idx
    neg_t_idx = neg_t_idx.reshape(-1, batch_size * repeats, 2)
    neg_t_idx.transpose_(0, 1)

    # sampling head
    head_weights = torch.stack(head_weights)
    random_h_idx = head_weights.multinomial(half_neg_num * repeats,
                                            replacement=True)
    random_h_idx = random_h_idx.t().flatten()
    # corrupt the first column
    head_batch_row_selector = torch.arange(batch_size * half_neg_num * repeats)
    head_batch_col_selector = torch.zeros(batch_size * half_neg_num * repeats, dtype=torch.long)  # corrupt tail
    # Fill the array of negative samples with the sampled random entities
    # at the tail positions
    neg_h_idx = idx.repeat((half_neg_num * repeats, 1))
    neg_h_idx[head_batch_row_selector, head_batch_col_selector] = random_h_idx
    neg_h_idx = neg_h_idx.reshape(-1, batch_size * repeats, 2)
    neg_h_idx.transpose_(0, 1)
    neg_idx = torch.cat((neg_t_idx, neg_h_idx), 1)
    return neg_idx


def list_to_dict(invalid_triples, i_rh2id=None, i_rt2id=None):
    # {r: {h: {t1, t2, t3}}}
    if i_rt2id is None:
        i_rt2id = {}
    if i_rh2id is None:
        i_rh2id = {}
    for row in invalid_triples:
        h = row[0]
        t = row[1]
        r = row[2]
        if r in i_rh2id:
            if h in i_rh2id[r]:
                i_rh2id[r][h].add(t)
            else:
                i_rh2id[r].update({h: {t}})
        else:
            i_rh2id.update({r: {h: {t}}})
        if r in i_rt2id:
            if t in i_rt2id[r]:
                i_rt2id[r][t].add(h)
            else:
                i_rt2id[r].update({t: {h}})
        else:
            i_rt2id.update({r: {t: {h}}})
    return i_rh2id, i_rt2id


class SchemaAwareGraphDataset(GraphDataset):
    """A Dataset storing the triples of a Knowledge Graph.

    Args:
        triples_file: str, path to the file containing triples. This is a
            text file where each line contains a triple of the form
            'subject predicate object'
        inconsistent_triples_file: str, path to the file containing inconsistent triples. This is a
            text file where each line contains a triple of the form
            'subject predicate object', it is the output of approximate consistency checking module
        write_maps_file: bool, if set to True, dictionaries mapping
            entities and relations to IDs are saved to disk (for reuse with
            other datasets).
    """

    def __init__(self, triples_file, inconsistent_triples_file,
                 dataset,
                 neg_samples=None, write_maps_file=False,
                 num_devices=1, schema_aware=False):
        """
        :param triples_file:
        :param inconsistent_triples_file:
        :param neg_samples:
        :param write_maps_file:
        :param num_devices:
        :param schema_aware:
        """
        super().__init__(triples_file, neg_samples, write_maps_file, num_devices)
        # Read triples and store as ints in tensor
        self.rh2tid, self.rt2hid = list_to_dict(self.triples.tolist())
        self.i_rh2tid = {}
        self.i_rt2hid = {}
        self.schema_aware = schema_aware
        if schema_aware:
            with open(inconsistent_triples_file) as neg_file:
                inconsistent_triples = []
                for i, line in enumerate(neg_file):
                    values = line.strip().split()
                    if len(values) > 3 and values[3] == '-1':
                        continue
                    head, rel, tail = line.split()[:3]
                    if head in self.entity2id and tail in self.entity2id and rel in self.rel2id:
                        inconsistent_triples.append([self.entity2id[head], self.entity2id[tail], self.rel2id[rel]])
            self.i_rh2tid, self.i_rt2hid = list_to_dict(inconsistent_triples)
            data_conf = DatasetConfig().get_config(dataset)
            abox_file_path = data_conf.input_dir + "abox_hrt_uri.txt"
            tmp_context_resource = ContextResources(abox_file_path, class_and_op_file_path=data_conf.input_dir,
                                                    work_dir="")
            abox_scanner_scheduler = AboxScannerScheduler(data_conf.tbox_patterns_dir, tmp_context_resource)
            abox_scanner_scheduler.register_patterns_rel([1, 2, 3, 4, 5, 6])
            self.neg_sampler = NegSampler(tmp_context_resource,
                                          abox_scanner_scheduler,
                                          self.entity2id, self.rel2id)

    def __getitem__(self, index):
        return self.triples[index]

    def __len__(self):
        return self.num_triples

    def collate_fn(self, data_list):
        """Given a batch of triples, return it together with a batch of
        corrupted triples where either the subject or object are replaced
        by a random entity. Use as a collate_fn for a DataLoader.
        """
        batch_size = len(data_list)
        pos_pairs, rels = torch.stack(data_list).split(2, dim=1)
        batch_entities = pos_pairs.reshape(batch_size * 2)
        self.neg_sampler.reasoning_for_neg_in_batch_entities(data_list=data_list,
                                                             batch_entities=batch_entities,
                                                             i_rh2tid=self.i_rh2tid,
                                                             i_rt2hid=self.i_rt2hid)
        neg_idx = get_schema_aware_neg_sampling_indices(data_list=data_list,
                                                        batch_entities=batch_entities,
                                                        rh2t=self.rh2tid,
                                                        rt2h=self.rt2hid,
                                                        i_rh2tid=self.i_rh2tid,
                                                        i_rt2hid=self.i_rt2hid,
                                                        batch_size=batch_size,
                                                        num_negatives=self.neg_samples,
                                                        schema_aware=self.schema_aware)
        return pos_pairs, rels, neg_idx


class SchemaAwareTextGraphDataset(SchemaAwareGraphDataset):
    """A dataset storing a graph, and textual descriptions of its entities.

    Args:
        triples_file: str, path to the file containing triples. This is a
            text file where each line contains a triple of the form
            'subject predicate object'
        max_len: int, maximum number of tokens to read per description.
        neg_samples: int, number of negative samples to get per triple
        tokenizer: transformers.PreTrainedTokenizer or GloVeTokenizer, used
            to tokenize the text.
        drop_stopwords: bool, if set to True, punctuation and stopwords are
            dropped from entity descriptions.
        write_maps_file: bool, if set to True, dictionaries mapping
            entities and relations to IDs are saved to disk (for reuse with
            other datasets).
        drop_stopwords: bool
    """

    def __init__(self, triples_file, inconsistent_triples_file, dataset, neg_samples, max_len, tokenizer,
                 drop_stopwords, write_maps_file=False, use_cached_text=False,
                 num_devices=1, schema_aware=False):
        super().__init__(triples_file, inconsistent_triples_file, dataset, neg_samples, write_maps_file,
                         num_devices, schema_aware=schema_aware)
        maps = torch.load(self.maps_path)
        ent_ids = maps['ent_ids']

        if max_len is None:
            max_len = tokenizer.max_len

        cached_text_path = osp.join(self.directory, 'text_data.pt')
        if use_cached_text:
            if osp.exists(cached_text_path):
                self.text_data = torch.load(cached_text_path)
                logger = logging.getLogger()
                logger.info(f'Loaded cached text data for'
                            f' {self.text_data.shape[0]} entities,'
                            f' and maximum length {self.text_data.shape[1]}.')
            else:
                raise LookupError(f'Cached text file not found at'
                                  f' {cached_text_path}')
        else:
            self.text_data = read_entity_text(ent_ids, max_len,
                                              text_directory=self.directory,
                                              drop_stopwords=drop_stopwords,
                                              tokenizer=tokenizer)

    def get_entity_description(self, ent_ids):
        """Get entity descriptions for a tensor of entity IDs."""
        text_data = self.text_data[ent_ids]
        text_end_idx = text_data.shape[-1] - 1

        # Separate tokens from lengths
        text_tok, text_len = text_data.split(text_end_idx, dim=-1)
        max_batch_len = text_len.max()
        # Truncate batch
        text_tok = text_tok[..., :max_batch_len]
        text_mask = (text_tok > 0).float()
        return text_tok, text_mask, text_len

    def collate_fn(self, data_list):
        """Given a batch of triples, return it in the form of
        entity descriptions, and the relation types between them.
        Use as a collate_fn for a DataLoader.
        """
        batch_size = len(data_list) // self.num_devices
        if batch_size <= 1:
            raise ValueError('collate_text can only work with batch sizes'
                             ' larger than 1.')

        pos_pairs, rels = torch.stack(data_list).split(2, dim=1)
        text_tok, text_mask, text_len = self.get_entity_description(pos_pairs)
        batch_entities = pos_pairs.reshape(batch_size * 2)
        neg_idx = get_schema_aware_neg_sampling_indices(data_list=data_list,
                                                        batch_entities=batch_entities,
                                                        rh2t=self.rh2tid,
                                                        rt2h=self.rt2hid,
                                                        i_rh2tid=self.i_rh2tid,
                                                        i_rt2hid=self.i_rt2hid,
                                                        batch_size=batch_size,
                                                        num_negatives=self.neg_samples,
                                                        repeats=self.num_devices, schema_aware=self.schema_aware)

        return text_tok, text_mask, rels, neg_idx


if __name__ == '__main__':
    pass
