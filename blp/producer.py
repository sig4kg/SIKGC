import gc
import os.path as osp

from blp.extend_models import *
import networkx as nx
import torch
from torch.optim import Adam
from torch.utils.data import DataLoader
from sacred.run import Run
from logging import Logger
from sacred import Experiment
from transformers import BertTokenizer, get_linear_schedule_with_warmup
import numpy as np
from module_utils.file_util import *
from data import GraphDataset, TextGraphDataset, GloVeTokenizer
from extend_data import SchemaAwareGraphDataset, SchemaAwareTextGraphDataset, MultiEpochsDataLoader
import models
import utils
import pandas as pd

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
ex = Experiment(save_git_info=False)
ex.logger = utils.get_logger()
NUM_WORKERS = 2


@ex.config
def config():
    work_dir = 'data/umls/'
    dataset = 'umls'
    inductive = False
    dim = 128
    model = 'transductive'
    # model = 'blp'
    rel_model = 'transe'
    loss_fn = 'margin'
    encoder_name = 'bert-base-cased'
    regularizer = 1e-2
    max_len = 32
    num_negatives = 12
    lr = 1e-3
    use_scheduler = True
    batch_size = 64
    emb_batch_size = 512
    eval_batch_size = 64
    max_epochs = 2
    checkpoint = None
    use_cached_text = True
    do_downstream_sample = False
    do_produce = True
    silver_eval = False
    schema_aware = False
    use_multi_epochs_loader = True


@ex.capture
@torch.no_grad()
def eval_link_prediction(model, triples_loader, text_dataset, entities,
                         epoch, emb_batch_size, _run: Run, _log: Logger,
                         prefix='', max_num_batches=None,
                         filtering_graph=None, new_entities=None,
                         return_embeddings=False):
    compute_filtered = filtering_graph is not None
    hit_positions = [1, 3, 10]
    hits_at_k = {pos: 0.0 for pos in hit_positions}
    mrr = 0.0
    hits_at_k_filt = {pos: 0.0 for pos in hit_positions}

    if device != torch.device('cpu'):
        model = model.module

    if isinstance(model, models.InductiveLinkPrediction):
        num_entities = entities.shape[0]
        if compute_filtered:
            max_ent_id = max(filtering_graph.nodes)
        else:
            max_ent_id = entities.max()
        ent2idx = utils.make_ent2idx(entities, max_ent_id)
    else:
        # Transductive models have a lookup table of embeddings
        num_entities = model.ent_emb.num_embeddings
        ent2idx = torch.arange(num_entities)
        entities = ent2idx

    # Create embedding lookup table for evaluation
    ent_emb = torch.zeros((num_entities, model.dim), dtype=torch.float,
                          device=device)
    idx = 0
    num_iters = np.ceil(num_entities / emb_batch_size)
    iters_count = 0
    while idx < num_entities:
        # Get a batch of entity IDs and encode them
        batch_ents = entities[idx:idx + emb_batch_size]
        if isinstance(model, models.InductiveLinkPrediction):
            # Encode with entity descriptions
            data = text_dataset.get_entity_description(batch_ents)
            text_tok, text_mask, text_len = data
            batch_emb = model(text_tok.unsqueeze(1).to(device),
                              text_mask.unsqueeze(1).to(device))
        else:
            # Encode from lookup table
            batch_emb = model.encode(batch_ents.to(device))

        ent_emb[idx:idx + batch_ents.shape[0]] = batch_emb

        iters_count += 1
        if iters_count % np.ceil(0.2 * num_iters) == 0:
            _log.info(f'[{idx + batch_ents.shape[0]:,}/{num_entities:,}]')

        idx += emb_batch_size

    ent_emb = ent_emb.unsqueeze(0)

    batch_count = 0
    _log.info('Computing metrics on set of triples')
    total = len(triples_loader) if max_num_batches is None else max_num_batches
    for i, triples in enumerate(triples_loader):
        if max_num_batches is not None and i == max_num_batches:
            break

        heads, tails, rels = torch.chunk(triples, chunks=3, dim=1)
        # Map entity IDs to positions in ent_emb
        heads = ent2idx[heads].to(device)
        tails = ent2idx[tails].to(device)
        assert heads.min() >= 0
        assert tails.min() >= 0
        # Embed triple
        head_embs = ent_emb.squeeze()[heads]
        tail_embs = ent_emb.squeeze()[tails]
        rel_embs = model.rel_emb(rels.to(device))

        # Score all possible heads and tails
        heads_predictions = model.score_fn(ent_emb, tail_embs, rel_embs)
        tails_predictions = model.score_fn(head_embs, ent_emb, rel_embs)

        pred_ents = torch.cat((heads_predictions, tails_predictions))
        true_ents = torch.cat((heads, tails))

        hits = utils.hit_at_k(pred_ents, true_ents, hit_positions)
        for j, h in enumerate(hits):
            hits_at_k[hit_positions[j]] += h
        mrr += utils.mrr(pred_ents, true_ents).mean().item()

        batch_count += 1
        if int(0.2 * total) != 0 and (i + 1) % int(0.2 * total) == 0:
            _log.info(f'[{i + 1:,}/{total:,}]')
        gc.collect()
        torch.cuda.empty_cache()

    for hits_dict in (hits_at_k, hits_at_k_filt):
        for k in hits_dict:
            hits_dict[k] /= batch_count

    mrr = mrr / batch_count
    log_str = f'{prefix} mrr: {mrr:.4f}  '
    _run.log_scalar(f'{prefix}_mrr', mrr, epoch)
    for k, value in hits_at_k.items():
        log_str += f'hits@{k}: {value:.4f}  '
        _run.log_scalar(f'{prefix}_hits@{k}', value, epoch)
    _log.info(log_str)

    if return_embeddings:
        out = (mrr, hits_at_k, ent_emb)
    else:
        out = (mrr, hits_at_k, None)
    return out


@ex.capture
@torch.no_grad()
def eval_and_get_score(model,
                       triples_loader,
                       text_dataset,
                       entities,
                       emb_batch_size,
                       work_dir,
                       _run: Run,
                       _log: Logger):
    use_gpu = False
    if device != torch.device('cpu'):
        model = model.module
        use_gpu = True

    if isinstance(model, models.InductiveLinkPrediction):
        num_entities = entities.shape[0]
        # if compute_filtered:
        #     max_ent_id = max(filtering_graph.nodes)
        # else:
        max_ent_id = entities.max()
        ent2idx = utils.make_ent2idx(entities, max_ent_id)
    else:
        # Transductive models have a lookup table of embeddings
        num_entities = model.ent_emb.num_embeddings
        ent2idx = torch.arange(num_entities)
        entities = ent2idx

    # Create embedding lookup table for evaluation
    ent_emb = torch.zeros((num_entities, model.dim), dtype=torch.float,
                          device=device)
    idx = 0
    num_iters = np.ceil(num_entities / emb_batch_size)
    iters_count = 0
    while idx < num_entities:
        # Get a batch of entity IDs and encode them
        batch_ents = entities[idx:idx + emb_batch_size]

        if isinstance(model, models.InductiveLinkPrediction):
            # Encode with entity descriptions
            data = text_dataset.get_entity_description(batch_ents)
            text_tok, text_mask, text_len = data
            batch_emb = model(text_tok.unsqueeze(1).to(device),
                              text_mask.unsqueeze(1).to(device))
        else:
            # Encode from lookup table
            batch_emb = model.encode(batch_ents.to(device))

        ent_emb[idx:idx + batch_ents.shape[0]] = batch_emb

        iters_count += 1
        if iters_count % np.ceil(0.2 * num_iters) == 0:
            _log.info(f'[{idx + batch_ents.shape[0]:,}/{num_entities:,}]')

        idx += emb_batch_size

    ent_emb = ent_emb.unsqueeze(0)

    all_sample_results = None
    for i, data in enumerate(triples_loader):
        # if max_num_batches is not None and i == max_num_batches:
        #     break
        if len(data) > 3:
            break
        pos_pairs, rels, neg_idx = data
        tmp_id2entid = pos_pairs.flatten().to(device)

        # positive pairs
        heads, tails = torch.chunk(pos_pairs, chunks=2, dim=1)
        # Map entity IDs to positions in ent_emb
        heads = ent2idx[heads].to(device)
        tails = ent2idx[tails].to(device)
        rels = rels.to(device)
        assert heads.min() >= 0
        assert tails.min() >= 0

        # Embed triple
        head_embs = ent_emb.squeeze()[heads]
        tail_embs = ent_emb.squeeze()[tails]
        rel_embs = model.rel_emb(rels)

        # Score all possible heads and tails
        pos_scores = model.score_fn(head_embs, tail_embs, rel_embs)
        pos_inds = torch.ones(pos_pairs.shape[0], 1).to(device)
        pos_result = torch.cat([heads, rels, tails, pos_scores, pos_inds], 1)
        if all_sample_results is None:
            all_sample_results = pos_result
        else:
            all_sample_results = torch.cat([all_sample_results, pos_result], 0)

        # negative pairs
        neg_rels = rels.repeat(1, neg_idx.shape[1]).reshape(neg_idx.shape[0] * neg_idx.shape[1], 1)
        neg_idx_pairs = torch.flatten(neg_idx, start_dim=0, end_dim=1)
        neg_heads_idx, neg_tails_idx = torch.chunk(neg_idx_pairs, chunks=2, dim=1)
        neg_heads = tmp_id2entid[neg_heads_idx]
        neg_tails = tmp_id2entid[neg_tails_idx]

        # Embed triple
        neg_head_embs = ent_emb.squeeze()[neg_heads]
        neg_tail_embs = ent_emb.squeeze()[neg_tails]
        neg_rel_embs = model.rel_emb(neg_rels)

        neg_scores = model.score_fn(neg_head_embs, neg_tail_embs, neg_rel_embs)
        neg_inds = torch.zeros(neg_heads_idx.shape[0], 1).to(device)
        neg_result = torch.cat([neg_heads, neg_rels, neg_tails, neg_scores, neg_inds], 1)
        all_sample_results = torch.cat([all_sample_results, neg_result], 0)
    torch.save(all_sample_results, work_dir + "sample_and_score.pt")


@ex.capture
@torch.no_grad()
def produce(model,
            triples_loader_hr,
            triples_loader_rt,
            text_dataset,
            entities,
            emb_batch_size,
            _run: Run,
            _log: Logger,
            return_embeddings=False,
            threshold=5):
    use_gpu = False
    if device != torch.device('cpu'):
        model = model.module
        use_gpu = True

    if isinstance(model, models.InductiveLinkPrediction):
        num_entities = entities.shape[0]
        max_ent_id = entities.max()
        ent2idx = utils.make_ent2idx(entities, max_ent_id)
    else:
        # Transductive models have a lookup table of embeddings
        num_entities = model.ent_emb.num_embeddings
        ent2idx = torch.arange(num_entities)
        entities = ent2idx

    # Create embedding lookup table for evaluation
    ent_emb = torch.zeros((num_entities, model.dim), dtype=torch.float,
                          device=device)
    idx = 0
    num_iters = np.ceil(num_entities / emb_batch_size)
    iters_count = 0
    while idx < num_entities:
        # Get a batch of entity IDs and encode them
        batch_ents = entities[idx:idx + emb_batch_size]

        if isinstance(model, models.InductiveLinkPrediction):
            # Encode with entity descriptions
            data = text_dataset.get_entity_description(batch_ents)
            text_tok, text_mask, text_len = data
            batch_emb = model(text_tok.unsqueeze(1).to(device),
                              text_mask.unsqueeze(1).to(device))
        else:
            # Encode from lookup table
            batch_emb = model.encode(batch_ents.to(device))

        ent_emb[idx:idx + batch_ents.shape[0]] = batch_emb

        iters_count += 1
        if iters_count % np.ceil(0.2 * num_iters) == 0:
            _log.info(f'[{idx + batch_ents.shape[0]:,}/{num_entities:,}]')

        idx += emb_batch_size
    ent_emb = ent_emb.unsqueeze(0)
    produced_triples = None
    k = 10
    entities = entities.to(device)
    for i, triples in enumerate(triples_loader_hr):
        heads, tails, rels = torch.chunk(triples, chunks=3, dim=1)
        # Map entity IDs to positions in ent_emb
        heads = ent2idx[heads].to(device, non_blocking=True)
        tails = ent2idx[tails].to(device, non_blocking=True)
        rels = rels.to(device, non_blocking=True)
        assert heads.min() >= 0
        assert tails.min() >= 0
        # Embed triple
        head_embs = ent_emb.squeeze()[heads]
        rel_embs = model.rel_emb(rels)
        # Score all possible tails
        tails_predictions = model.score_fn(head_embs, ent_emb, rel_embs)
        scores_t, indices_t = tails_predictions.topk(k=k)
        truth_t_index = (indices_t == tails).nonzero()
        truth_score_t = torch.empty(triples.shape[0], dtype=torch.float32).fill_(-999.).to(device)
        truth_score_t_values = scores_t[(indices_t == tails).nonzero(as_tuple=True)]
        truth_score_t.index_put_((truth_t_index[:, 0],), truth_score_t_values)
        pred_idx_at_k = indices_t[:, :k]
        pred_t_k_hit = torch.chunk(pred_idx_at_k, chunks=k, dim=1)  # each column is a list of hit for all triples
        score_t_k = torch.chunk(scores_t, chunks=k, dim=1)
        for column_index, t in enumerate(pred_t_k_hit):
            tokeep_indices = (score_t_k[column_index].view(triples.shape[0], ) >= truth_score_t - threshold).nonzero(

                as_tuple=True)  # x <= true + threshole   -> -x >= -true -threshole  ->
            tmp_hrts = torch.cat([entities[heads], rels, entities[t], score_t_k[column_index]], 1)
            fitered_hrts = tmp_hrts[tokeep_indices]
            produced_triples = fitered_hrts if produced_triples is None else torch.cat([produced_triples, fitered_hrts])
    for i, triples in enumerate(triples_loader_rt):
        heads, tails, rels = torch.chunk(triples, chunks=3, dim=1)
        # Map entity IDs to positions in ent_emb
        heads = ent2idx[heads].to(device, non_blocking=True)
        tails = ent2idx[tails].to(device, non_blocking=True)
        rels = rels.to(device, non_blocking=True)
        assert heads.min() >= 0
        assert tails.min() >= 0
        # Embed triple
        tail_embs = ent_emb.squeeze()[tails]
        rel_embs = model.rel_emb(rels)
        # Score all possible heads and tails
        heads_predictions = model.score_fn(ent_emb, tail_embs, rel_embs)
        scores_h, indices_h = heads_predictions.topk(k=k)
        truth_h_index = (indices_h == heads).nonzero()
        truth_score_h = torch.empty(triples.shape[0], dtype=torch.float32).fill_(-999.).to(device)
        truth_score_h_values = scores_h[(indices_h == heads).nonzero(as_tuple=True)]
        truth_score_h.index_put_((truth_h_index[:, 0],), truth_score_h_values)
        pred_idx_at_k = indices_h[:, :k]
        pred_h_k_hit = torch.chunk(pred_idx_at_k, chunks=k, dim=1)  # each column is a list of hit for all triples
        score_h_k = torch.chunk(scores_h, chunks=k, dim=1)

        for column_index, h in enumerate(pred_h_k_hit):
            tokeep_indices = (score_h_k[column_index].view(triples.shape[0], ) >= truth_score_h - threshold).nonzero(
                as_tuple=True)  # true_score + threshold >= pred
            tmp_hrts = torch.cat([entities[h], rels, entities[tails], score_h_k[column_index]], 1)
            fitered_hrts = tmp_hrts[tokeep_indices]
            produced_triples = fitered_hrts if produced_triples is None else torch.cat([produced_triples, fitered_hrts])
    # read to cpu and ready to output
    if use_gpu:
        produced_triples = produced_triples.cpu()
        ent_emb = ent_emb.cpu()

    if return_embeddings:
        return produced_triples, ent_emb
    else:
        return produced_triples, None


@ex.command
def link_prediction(dataset, inductive, dim, model, rel_model, loss_fn,
                    encoder_name, regularizer, max_len, num_negatives, lr,
                    use_scheduler, batch_size, emb_batch_size, eval_batch_size,
                    max_epochs, checkpoint, use_cached_text, work_dir, do_downstream_sample, do_produce, silver_eval,
                    _run: Run, _log: Logger,
                    schema_aware, use_multi_epochs_loader):
    drop_stopwords = model in {'bert-bow', 'bert-dkrl',
                               'glove-bow', 'glove-dkrl'}

    prefix = 'ind-' if inductive and model != 'transductive' else ''
    triples_file = f'{work_dir}{prefix}train.tsv'
    _log.info(torch.__version__)
    _log.info(f"Is cuda available? {torch.cuda.is_available()}")
    _log.info(f"device: {device}")
    if device != torch.device('cpu'):
        num_devices = torch.cuda.device_count()
        if batch_size % num_devices != 0:
            raise ValueError(f'Batch size ({batch_size}) must be a multiple of'
                             f' the number of CUDA devices ({num_devices})')
        _log.info(f'CUDA devices used: {num_devices}')
    else:
        num_devices = 1
        _log.info('Training on CPU')

    inconsistent_triples_file = f'{work_dir}invalid_hrt.txt'
    if model == 'transductive':
        if schema_aware:
            train_data = SchemaAwareGraphDataset(triples_file,
                                                 inconsistent_triples_file,
                                                 dataset=dataset,
                                                 neg_samples=num_negatives,
                                                 write_maps_file=True,
                                                 num_devices=num_devices,
                                                 schema_aware=schema_aware)
        else:
            train_data = GraphDataset(triples_file, num_negatives,
                                      write_maps_file=True,
                                      num_devices=num_devices)
    else:
        if model.startswith('bert') or model == 'blp':
            bert_path = "../saved_models/bert-base-cased"
            local_models = Path(bert_path)
            if local_models.exists():
                tokenizer = BertTokenizer.from_pretrained(os.path.join(bert_path, "vocab.txt"))
            else:
                tokenizer = BertTokenizer.from_pretrained(encoder_name)
        elif model == 'fasttext':
            tokenizer = FastTextTokenizer()
        else:
            tokenizer = GloVeTokenizer('data/glove/glove.6B.300d-maps.pt')
        if schema_aware:
            train_data = SchemaAwareTextGraphDataset(triples_file,
                                                     inconsistent_triples_file,
                                                     dataset=dataset,
                                                     neg_samples=num_negatives,
                                                     max_len=max_len,
                                                     tokenizer=tokenizer,
                                                     drop_stopwords=drop_stopwords,
                                                     write_maps_file=True,
                                                     use_cached_text=use_cached_text,
                                                     num_devices=num_devices,
                                                     schema_aware=schema_aware)
        else:
            train_data = TextGraphDataset(triples_file, num_negatives,
                                          max_len, tokenizer, drop_stopwords,
                                          write_maps_file=True,
                                          use_cached_text=use_cached_text,
                                          num_devices=num_devices)

    loader_class = torch.utils.data.DataLoader
    if use_multi_epochs_loader:
        loader_class = MultiEpochsDataLoader
    train_loader = loader_class(train_data, batch_size, shuffle=True,
                                collate_fn=train_data.collate_fn, pin_memory=True,
                                num_workers=NUM_WORKERS, drop_last=True)
    valid_data = GraphDataset(f'{work_dir}{prefix}dev.tsv')
    valid_loader = loader_class(valid_data, eval_batch_size, num_workers=NUM_WORKERS, pin_memory=True)
    test_data_hr = GraphDataset(f'{work_dir}test_hr.tsv')
    test_loader_hr = loader_class(test_data_hr, eval_batch_size, pin_memory=True, num_workers=NUM_WORKERS)
    test_data_rt = GraphDataset(f'{work_dir}test_rt.tsv')
    test_loader_rt = loader_class(test_data_rt, eval_batch_size, pin_memory=True, num_workers=NUM_WORKERS)

    graph = nx.MultiDiGraph()
    all_triples = torch.cat((train_data.triples,
                             valid_data.triples,
                             test_data_hr.triples,
                             test_data_rt.triples))
    graph.add_weighted_edges_from(all_triples.tolist())

    train_ent = set(train_data.entities.tolist())
    train_val_ent = set(valid_data.entities.tolist()).union(train_ent)
    train_val_test_ent = set(test_data_hr.entities.tolist()).union(train_val_ent)
    train_val_test_ent = set(test_data_rt.entities.tolist()).union(train_val_test_ent)

    # train_ent = torch.tensor(list(train_ent))
    train_val_ent = torch.tensor(list(train_val_ent))
    train_val_test_ent = torch.tensor(list(train_val_test_ent))

    model = utils.get_model(model, dim, rel_model, loss_fn,
                            len(train_val_test_ent), train_data.num_rels,
                            encoder_name, regularizer)

    if device != torch.device('cpu'):
        model = torch.nn.DataParallel(model).to(device)
    _log.info(f"model device: {next(model.parameters()).device}")

    optimizer = Adam(model.parameters(), lr=lr)
    total_steps = len(train_loader) * max_epochs
    if use_scheduler:
        warmup = int(0.2 * total_steps)
        scheduler = get_linear_schedule_with_warmup(optimizer,
                                                    num_warmup_steps=warmup,
                                                    num_training_steps=total_steps)
    best_valid_mrr = 0.0
    last_valid_mrr = 0.0
    best_hit_at_k = {}
    early_stop_sign = 0
    checkpoint_file = osp.join(work_dir, f'checkpoint.pt')
    for epoch in range(1, max_epochs + 1):
        train_loss = 0
        for step, data in enumerate(train_loader):
            if device != torch.device('cpu'):
                if len(data) == 3:
                    pos_pairs, rels, neg_idx = data[0], data[1], data[2]
                    pos_pairs = pos_pairs.to(device, non_blocking=True)
                    rels = rels.to(device, non_blocking=True)
                    neg_idx = neg_idx.to(device, non_blocking=True)
                    loss = model(pos_pairs, rels, neg_idx).mean()
                elif len(data) == 4:
                    text_tok, text_mask, rels, neg_idx = data[0], data[1], data[2], data[3]
                    text_tok = text_tok.to(device, non_blocking=True)
                    text_mask = text_mask.to(device, non_blocking=True)
                    rels = rels.to(device, non_blocking=True)
                    neg_idx = neg_idx.to(device, non_blocking=True)
                    loss = model(text_tok, text_mask, rels, neg_idx).mean()
                del data

            else:
                loss = model(*data).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if use_scheduler:
                scheduler.step()

            train_loss += loss.item()

            if step % int(0.05 * len(train_loader)) == 0:
                _log.info(f'Epoch {epoch}/{max_epochs} '
                          f'[{step}/{len(train_loader)}]: {loss.item():.6f}')
                _run.log_scalar('batch_loss', loss.item())

            gc.collect()
            torch.cuda.empty_cache()

        _run.log_scalar('train_loss', train_loss / len(train_loader), epoch)

        _log.info('Evaluating on validation set')
        val_mrr, hit_at_k, _ = eval_link_prediction(model, valid_loader, train_data,
                                                    train_val_ent, epoch,
                                                    emb_batch_size, prefix='valid')

        # Keep checkpoint of best performing model (based on raw MRR)
        if val_mrr > best_valid_mrr:
            best_valid_mrr = val_mrr
            best_hit_at_k = hit_at_k
            early_stop_sign = 0
            torch.save(model.state_dict(), checkpoint_file)
        if val_mrr <= last_valid_mrr:
            early_stop_sign += 1

        if early_stop_sign >= 10:
            break
        last_valid_mrr = val_mrr

    log_file_name = work_dir + "blp_eval.log"
    log_str = f"-------blp training eval---------\nmrr: {best_valid_mrr}\n"
    for k, value in best_hit_at_k.items():
        log_str += f'hits@{k}: {value:.4f}\n'
    save_to_file(log_str, log_file_name, mode='a')
    # Evaluate with best performing checkpoint
    if max_epochs > 0:
        model.load_state_dict(torch.load(checkpoint_file))

    if do_downstream_sample:
        _log.info('get sample and score for Ricky...')
        train_eval_loader2 = DataLoader(train_data, batch_size, shuffle=True,
                                        collate_fn=train_data.collate_fn, pin_memory=True,
                                        num_workers=NUM_WORKERS, drop_last=True)
        eval_and_get_score(model=model,
                           triples_loader=train_eval_loader2,
                           text_dataset=train_data,
                           entities=train_val_test_ent,
                           emb_batch_size=emb_batch_size,
                           work_dir=work_dir)
    if silver_eval:
        valid_data_silver = GraphDataset(f'{work_dir}test_rel_silver.tsv')
        valid_loader_silver = DataLoader(valid_data_silver, eval_batch_size, pin_memory=True, num_workers=NUM_WORKERS)
        val_mrr, hit_at_k, ent_emb = eval_link_prediction(model, valid_loader_silver, train_data,
                                                          train_val_ent, 0,
                                                          emb_batch_size, prefix='valid', return_embeddings=True)
        log_str = '-------blp eval on rel silver test set ---------\n'
        for k, value in hit_at_k.items():
            log_str += f'hits@{k}: {value:.4f}\n'
        log_str += f"mrr: {val_mrr}\n"
        save_to_file(log_str, log_file_name, mode='a')
        # Save final entity embeddings obtained with trained encoder
        torch.save(ent_emb, osp.join(work_dir, f'ent_emb.pt'))
        torch.save(train_val_test_ent, osp.join(work_dir, f'ents.pt'))

    if do_produce:
        _log.info('Produce new triples...')
        produced_triples_with_scores, ent_emb = produce(model=model,
                                                        triples_loader_hr=test_loader_hr,
                                                        triples_loader_rt=test_loader_rt,
                                                        text_dataset=train_data,
                                                        entities=train_val_test_ent,
                                                        emb_batch_size=emb_batch_size,
                                                        return_embeddings=True,
                                                        threshold=5)
        tris = produced_triples_with_scores.detach().numpy()
        df_tris = pd.DataFrame(tris, columns=['h', 'r', 't', 's'])
        df_tris = df_tris.astype({'h': int, 'r': int, 't': int}).groupby(['h', 'r', 't'])['s'].max().reset_index()
        df_tris[['h', 'r', 't']] = df_tris[['h', 'r', 't']].astype(int)
        df_tris = df_tris.sort_values(by='s', axis=0, ascending=False).drop_duplicates(['h', 'r', 't'], keep='first')
        id2entity = dict((v, k) for k, v in train_data.entity2id.items())
        id2rel = dict((v, k) for k, v in train_data.rel2id.items())
        df_tris[['r']] = df_tris[['r']].applymap(lambda x: id2rel[x])  # to string
        df_tris[['h', 't']] = df_tris[['h', 't']].applymap(lambda x: id2entity[x])  # to string
        df_tris.to_csv(osp.join(work_dir, f'blp_new_triples.csv'), header=False, index=False, sep='\t', mode='a')
        # Save final entity embeddings obtained with trained encoder
        torch.save(ent_emb, osp.join(work_dir, f'ent_emb.pt'))
        torch.save(train_val_test_ent, osp.join(work_dir, f'ents.pt'))


@ex.automain
def my_main():
    link_prediction()


if __name__ == '__main__':
    ex.run()
