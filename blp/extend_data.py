import copy
import random
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from prefetch_generator import BackgroundGenerator
import file_util
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
                 abox_scanner_scheduler: AboxScannerScheduler, inconsistent_triples_file, num_negs,
                 blp_ent2id, blp_rel2id, input_dir, dynamic_negs=False, schema_aware=False, pre_negs=False):
        self.context_resource = context_resource
        self.abox_scanner_scheduler = abox_scanner_scheduler
        self.blp_ent2id = blp_ent2id
        self.context2blp_entid, self.blp2context_entid, self.context2blp_relid, self.blp2context_relid = \
            get_maps_context2blpid(context_resource, blp_ent2id, blp_rel2id)
        self.dynamic_negs = dynamic_negs
        self.schema_aware = schema_aware
        self.pre_negs = pre_negs
        self.rh2t, self.rt2h = {}, {}
        self.i_rh2t, self.i_rt2h = {}, {}
        self.n_rh2t, self.n_rt2h = {}, {}
        self.input_dir = input_dir
        self.num_negs = num_negs
        self.inconsistent_triples_file = inconsistent_triples_file
        self.num_entities = len(self.blp_ent2id)

    def load_pre_generated_negs(self):
        self.rh2t, self.rt2h = self._context_hrt2blp_dict(self.context_resource.hrt_int_df)
        if self.schema_aware:
            self.i_rh2t, self.i_rt2h = self._hrt_file2blp_dict(self.inconsistent_triples_file)
        if self.pre_negs:
            self._pre_negs2blp_dict()

    def _dynamic_generation(self, data_list, batch_entities):
        candidate_ents_contextid = [self.blp2context_entid[e] for e in torch.unique(batch_entities).tolist()]
        sample_count = len(candidate_ents_contextid)
        sample_count = self.num_neg * 2 if self.num_neg * 2 < sample_count else sample_count
        pos_htr_int = pd.DataFrame(data=data_list, columns=['head', 'tail', 'rel']).applymap(lambda x: x.item()).copy()
        pos_htr_int['head'] = pos_htr_int['head'].apply(lambda x: self.blp2context_entid[x])
        pos_htr_int['tail'] = pos_htr_int['tail'].apply(lambda x: self.blp2context_entid[x])
        pos_htr_int['rel'] = pos_htr_int['rel'].apply(lambda x: self.blp2context_relid[x])
        pos_examples_df = pos_htr_int[['head', 'rel', 'tail']]  # make copy
        corrupt1 = pd.DataFrame()
        corrupt1['c_h'] = pos_examples_df['head'].apply(
            func=lambda x: random.sample(candidate_ents_contextid, sample_count))
        corrupt1['rel'] = pos_examples_df['rel']
        corrupt1['tail'] = pos_examples_df['tail']
        corrupt1.reset_index(drop=True)

        corrupt2 = pd.DataFrame()
        corrupt2['head'] = pos_examples_df['head']
        corrupt2['rel'] = pos_examples_df['rel']
        corrupt2['c_t'] = pos_examples_df['tail'].apply(
            func=lambda x: random.sample(candidate_ents_contextid, sample_count))
        corrupt2.reset_index(drop=True)

        def explode(tmp_df, col, rename_col) -> pd.DataFrame:
            tmp_df[col] = tmp_df[col].apply(lambda x: list(x))
            tm = pd.DataFrame(list(tmp_df[col])).stack().reset_index(level=0)
            tm = tm.rename(columns={0: rename_col}).join(tmp_df, on='level_0'). \
                drop(axis=1, labels=[col, 'level_0']).reset_index(drop=True)
            return tm

        corrupt1 = explode(corrupt1, "c_h", "head").dropna(how='any').astype('int64')
        corrupt2 = explode(corrupt2, "c_t", "tail").dropna(how='any').astype('int64')
        to_scan_df = pd.concat([pos_examples_df, corrupt1, corrupt2]).drop_duplicates(keep="first").reset_index(
            drop=True)
        self.context_resource.hrt_to_scan_df = to_scan_df
        self.context_resource.hrt_int_df = pos_examples_df
        _, inv = self.abox_scanner_scheduler.scan_rel_IJPs(work_dir="", save_result=False, log_process=False)
        return inv

    def _context_hrt2blp_dict(self, hrt_df):
        hrt_df['head'] = hrt_df['head'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        hrt_df['tail'] = hrt_df['tail'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        hrt_df['rel'] = hrt_df['rel'].apply(
            lambda x: self.context2blp_relid[x] if x in self.context2blp_relid else np.nan)
        hrt_df = hrt_df.dropna(how='any').astype('int64')
        return df_to_dict(hrt_df)

    def _hrt_file2blp_dict(self, file):
        invalid_hrt_df = file_util.read_hrt_2_hrt_int_df(file)
        return self._context_hrt2blp_dict(invalid_hrt_df)

    def _pre_negs2blp_dict(self):
        rh2t = dict()
        rt2h = dict()
        with open(self.input_dir + "pred_negs_hr.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                hr, neg_t = line.strip().split('\t')
                hr = hr.split(', ')
                h, r = int(hr[0]), int(hr[1])
                if h not in self.context2blp_entid or r not in self.context2blp_relid:
                    continue
                h, r = self.context2blp_entid[h], self.context2blp_relid[r]
                neg_t = neg_t.split(";")
                neg_t = [self.context2blp_entid[int(t)] for t in neg_t if int(t) in self.context2blp_entid]
                if r in rh2t:
                    rh2t[r].update({h: neg_t})
                else:
                    rh2t.update({r: {h: neg_t}})
        self.n_rh2t, self.n_rt2h = rh2t, rt2h

    def _reasoning_for_neg_in_batch_entities(self, data_list,
                                             batch_entities):
        inv = self._dynamic_generation(data_list, batch_entities)
        inv_blp_df = inv.drop_duplicates(keep='first').reset_index(drop=True)
        inv_blp_df['head'] = inv_blp_df['head'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        inv_blp_df['tail'] = inv_blp_df['tail'].apply(
            lambda x: self.context2blp_entid[x] if x in self.context2blp_entid else np.nan)
        inv_blp_df['rel'] = inv_blp_df['rel'].apply(
            lambda x: self.context2blp_relid[x] if x in self.context2blp_relid else np.nan)
        inv_blp_df = inv_blp_df.dropna(how='any').astype('int64')
        return df_to_dict(inv_blp_df)

    def get_schema_aware_neg_sampling_indices(self, data_list,
                                              batch_entities,
                                              batch_size):
        if self.dynamic_negs:
            batch_rh2tid, batch_rt2hid = self._reasoning_for_neg_in_batch_entities(data_list, batch_entities)
        batch_entities_np = batch_entities.numpy()
        # idx = torch.arange(self.num_entities).reshape(batch_size, 2)  # n rows, 2 columns
        half_neg_num = int(self.num_negs / 2)
        # for each row, generate half_neg_num head neg samples and  half_neg_num tail neg samples
        # sample head
        # fill with inconsistent triples first, then fill the left with random entities
        # fill with pre-generated negatives
        # For each row, sample entities, assigning 0 probability to entities of the same row
        tail_weights = []
        head_weights = []
        for row_idx, row in enumerate(data_list):
            # corrupt tail, basic sampling weight for each entity in batch
            row_tail_weights = torch.ones(self.num_entities, dtype=torch.float)
            # corrupt head, basic sampling weight for each entity in batch
            row_head_weights = torch.ones(self.num_entities, dtype=torch.float)
            # row_zeros = torch.zeros(2)  # same dim as idx, per row
            # row_ent_idx = idx[row_idx]
            # row_tail_weights.scatter_(0, row_ent_idx, row_zeros)
            h, t, r = row[0].item(), row[1].item(), row[2].item()
            # corrupt tail
            # exclude pos triples
            if r in self.rh2t:
                rh = self.rh2t[r]
                if h in rh:
                    pos_t = rh[h]
                    pos_t_ent_idx = torch.tensor(pos_t, dtype=torch.int64)
                    row_t_zeros_pos = torch.full(pos_t_ent_idx.shape, fill_value=0.0)
                    row_tail_weights.scatter_(0, pos_t_ent_idx, row_t_zeros_pos)
            if r in self.rt2h:
                rt = self.rt2h[r]
                if t in rt:
                    pos_h = rt[t]
                    pos_h_ent_idx = torch.tensor(pos_h, dtype=torch.int64)
                    row_h_zeros_pos = torch.full(pos_h_ent_idx.shape, fill_value=0.0)
                    row_head_weights.scatter_(0, pos_h_ent_idx, row_h_zeros_pos)
            # set weight 2 for inconsistent triples
            if self.schema_aware:
                if r in self.i_rh2t:
                    i_rh = self.i_rh2t[r]
                    if h in i_rh:
                        candidate_neg_t = i_rh[h]
                        # inco_t_ent_idx = [key for key, val in enumerate(batch_entities_np) if val in candidate_neg_t]
                        inco_t_ent_idx = torch.tensor(candidate_neg_t, dtype=torch.int64)
                        row_t_twos = torch.full(inco_t_ent_idx.shape, fill_value=2.0)
                        row_tail_weights.scatter_(0, inco_t_ent_idx, row_t_twos)
                if r in self.i_rt2h:
                    i_rt = self.i_rt2h[r]
                    if t in i_rt:
                        candidate_neg_h = i_rt[t]
                        inco_h_ent_idx = torch.tensor(candidate_neg_h, dtype=torch.int64)
                        row_h_twos = torch.full(inco_h_ent_idx.shape, fill_value=2.0)
                        row_head_weights.scatter_(0, inco_h_ent_idx, row_h_twos)
            if self.pre_negs:
                if r in self.n_rh2t:
                    n_rh = self.n_rh2t[r]
                    if h in n_rh:
                        candidate_neg_t = n_rh[h]
                        neg_t_ent_idx = torch.tensor(candidate_neg_t, dtype=torch.int64)
                        row_t_tens = torch.full(neg_t_ent_idx.shape, fill_value=10.0)
                        row_tail_weights.scatter_(0, neg_t_ent_idx, row_t_tens)
                if r in self.n_rt2h:
                    n_rt = self.n_rt2h[r]
                    if t in n_rt:
                        candidate_neg_h = n_rt[t]
                        neg_h_ent_idx = torch.tensor(candidate_neg_h, dtype=torch.int64)
                        row_h_tens = torch.full(neg_h_ent_idx.shape, fill_value=10.0)
                        row_head_weights.scatter_(0, neg_h_ent_idx, row_h_tens)
            tail_weights.append(row_tail_weights)
            head_weights.append(row_head_weights)
        # sampling  tail
        tail_weights = torch.stack(tail_weights)
        random_t_idx = tail_weights.multinomial(half_neg_num,
                                                replacement=True)
        random_t_idx = random_t_idx.t().flatten()
        # corrupt the second column
        tail_batch_row_selector = torch.arange(batch_size * half_neg_num)
        tail_batch_col_selector = torch.ones(batch_size * half_neg_num, dtype=torch.long)  # corrupt tail
        # Fill the array of negative samples with the sampled random entities
        # at the tail positions
        neg_t_idx = idx.repeat((half_neg_num, 1))
        neg_t_idx[tail_batch_row_selector, tail_batch_col_selector] = random_t_idx
        neg_t_idx = neg_t_idx.reshape(-1, batch_size, 2)
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


def df_to_dict(invalid_triples_df):
    # {r: {h: {t1, t2, t3}}}
    agg_rh = invalid_triples_df.groupby(['rel', 'head'], as_index=False).agg({'tail': lambda x: list(x)})
    rh_df = agg_rh.set_index(['rel', 'head']).unstack(level=0).droplevel(level=0, axis=1)
    tmp_i_rh2id = {col: rh_df[col].dropna().to_dict() for col in rh_df}
    # {r: {t: {h1, h2, h3}}}
    agg_rt = invalid_triples_df.groupby(['rel', 'tail'], as_index=False).agg({'head': lambda x: list(x)})
    rt_df = agg_rt.set_index(['rel', 'tail']).unstack(level=0).droplevel(level=0, axis=1)
    tmp_i_rt2id = {col: rt_df[col].dropna().to_dict() for col in rt_df}
    return tmp_i_rh2id, tmp_i_rt2id


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

    def __init__(self, triples_file,
                 dataset, inconsistent_triples_file, write_maps_file=False, num_negs=16,
                 num_devices=1, schema_aware=False, pre_negs=False, dynamic_negs=False):
        """
        :param triples_file:
        :param inconsistent_triples_file:
        :param neg_samples:
        :param write_maps_file:
        :param num_devices:
        :param schema_aware:
        """
        super().__init__(triples_file, num_negs, write_maps_file, num_devices)
        # Read triples and store as ints in tensor
        # self.rh2tid, self.rt2hid = df_to_dict(pd.DataFrame(data=self.triples.tolist(), columns=['head', 'tail', 'rel']))
        self.schema_aware = schema_aware
        self.dynamic_negs = dynamic_negs
        self.pre_negs = pre_negs
        data_conf = DatasetConfig().get_config(dataset)
        tmp_context_resource = ContextResources(data_conf.input_dir + "abox_hrt_uri.txt",
                                                class_and_op_file_path=data_conf.input_dir,
                                                work_dir="")
        tmp_context_resource.hrt_int_df = tmp_context_resource.hrt_to_scan_df
        abox_scanner_scheduler = AboxScannerScheduler(data_conf.tbox_patterns_dir, tmp_context_resource)
        abox_scanner_scheduler.register_patterns_rel([1, 2, 3, 4, 5, 6])
        self.neg_sampler = NegSampler(context_resource=tmp_context_resource,
                                      abox_scanner_scheduler=abox_scanner_scheduler,
                                      inconsistent_triples_file=inconsistent_triples_file,
                                      num_negs=num_negs,
                                      blp_ent2id=self.entity2id,
                                      blp_rel2id=self.rel2id,
                                      input_dir=data_conf.input_dir,
                                      dynamic_negs=dynamic_negs,
                                      schema_aware=schema_aware,
                                      pre_negs=pre_negs)
        self.neg_sampler.load_pre_generated_negs()

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
        neg_idx = self.neg_sampler.get_schema_aware_neg_sampling_indices(data_list=data_list,
                                                                         batch_entities=batch_entities,
                                                                         batch_size=batch_size)
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
                 num_devices=1, schema_aware=False, dynamic_negs=False):
        super().__init__(triples_file, inconsistent_triples_file, dataset, neg_samples, write_maps_file,
                         num_devices, schema_aware=schema_aware)
        maps = torch.load(self.maps_path)
        ent_ids = maps['ent_ids']
        num_entities = len(ent_ids)
        self.dynamic_negs = dynamic_negs

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
        neg_idx = None
        return text_tok, text_mask, rels, neg_idx


class MultiEpochsDataLoader(DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._DataLoader__initialized = False
        self.batch_sampler = _RepeatSampler(self.batch_sampler)
        self._DataLoader__initialized = True
        self.iterator = BackgroundGenerator(super().__iter__())
        # self.iterator = super().__iter__()

    def __len__(self):
        return len(self.batch_sampler.sampler)

    def __iter__(self):
        for i in range(len(self)):
            yield next(self.iterator)


class _RepeatSampler(object):
    """ Sampler that repeats forever.
    Args:
        sampler (Sampler)
    """

    def __init__(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        while True:
            yield from iter(self.sampler)


if __name__ == '__main__':
    tt = pd.DataFrame(data=[[0, 1, 2], [0, 1, 3], [4, 1, 3], [0, 2, 5]], columns=['head', 'rel', 'tail'])
    print(tt)
    agg_rh = tt.groupby(['rel', 'head'], as_index=False).agg({'tail': lambda x: list(x)})
    new_df = agg_rh.set_index(['rel', 'head']).unstack(level=0).droplevel(level=0, axis=1)
    d = {col: new_df[col].dropna().to_dict() for col in new_df}
    print(d)
    # agg_rh = tt.groupby(['rel', 'head'], as_index=False).agg({'tail': lambda x: list(x)})
    # print(agg_rh)
    # agg_r = tt.groupby(['rel'], as_index=False).agg({'head': lambda x: list(x)})
    # print(agg_r)
