import pandas as pd
from tqdm import tqdm
import traceback
from abox_scanner.ContextResources import ContextResources
from file_util import read_hrt_2_hrt_int_df
from pipelines.pipeline_util import prepare_context
import openai
import re
from openai_multi_client import OpenAIMultiClient

# Remember to set the OPENAI_API_KEY environment variable to your API key
api = OpenAIMultiClient(endpoint="chats", data_template={"model": "gpt-3.5-turbo"})


# def make_requests(pred_hr, context_resource):
#     for idx, row in tqdm(pred_hr.iterrows()):
#         h = row['head']
#         r = row['rel']
#         t = row['tail']
#         if h in context_resource.entid2text and r in context_resource.relid2text:
#             pred_text = [context_resource.entid2text[p] for p in t if p in context_resource.entid2text]
#             prompt_t_template = f'''Rank candidates among [{'; '.join(pred_text[:10])}] based on the relevance to the query <{context_resource.entid2text[h]}, {context_resource.relid2text[r]}, ?>, with a score range of [0-1] where 1 the true. list result only.'''
#             api.request(data={
#                 "messages": [{
#                     "role": "user",
#                     "content": prompt_t_template
#                 }]
#             }, metadata={'h': h, 'r':r})
#
#
# def chunker(seq, size):
#     for pos in range(0, len(seq), size):
#         yield seq.iloc[pos:pos + size], pos + size

#
# def multi_request_generate_neg_candidates(input_dir, out_file, start_count=0):
#     # initialize context resource
#     abox_file_path = input_dir + "abox_hrt_uri.txt"
#     pred_file_path = input_dir + "correct_hrt.txt"
#     context_resource = ContextResources(abox_file_path, class_and_op_file_path=input_dir,
#                                         work_dir=input_dir)
#     pred_df = read_hrt_2_hrt_int_df(pred_file_path)
#     true_df = context_resource.hrt_to_scan_df
#     pred_df = pd.concat([pred_df, true_df, true_df]).drop_duplicates(keep=False)
#     # true_df_hr = true_df.groupby(['h', 'r'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
#     pred_hr = pred_df.groupby(['head', 'rel'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
#     pred_hr = pred_hr.iloc[start_count:]
#     context_resource.load_id2literal()
#     neg_list = []
#     text2id = {context_resource.entid2text[i]: i for i in context_resource.entid2text}
#     chunk_size = 10
#     for i_df, pos in tqdm(chunker(pred_hr, chunk_size)):
#         api.run_request_function(make_requests, i_df, context_resource)
#         for result in api:
#             h = result.metadata['h']
#             r = result.metadata['r']
#             assistant_reply = result.response['choices'][0]['message']['content']
#             negs = unwrap_reply(assistant_reply, text2id)
#             if len(negs) > 0:
#                 neg_list.append([h, r, negs])
#         if len(neg_list) == 0:
#             continue
#         with open(out_file, 'a') as f:
#             for item in neg_list:
#                 f.write(f"{str(item[0])}, {str(item[1])}\t{';'.join([str(neg_i) for neg_i in item[2]])}\n")
#             neg_list.clear()
#             print(f"at pos: {pos}")


def generate_neg_candidates_hr(input_dir, out_file, start_count=0):
    # initialize context resource
    abox_file_path = input_dir + "abox_hrt_uri.txt"
    pred_file_path = input_dir + "correct_hrt.txt"
    context_resource = ContextResources(abox_file_path, class_and_op_file_path=input_dir,
                                        work_dir=input_dir)
    pred_df = read_hrt_2_hrt_int_df(pred_file_path)
    true_df = context_resource.hrt_to_scan_df
    pred_df = pd.concat([pred_df, true_df, true_df]).drop_duplicates(keep=False)
    # true_df_hr = true_df.groupby(['h', 'r'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    pred_hr = pred_df.groupby(['head', 'rel'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    context_resource.load_id2literal()
    neg_list = []
    text2id = {context_resource.entid2text[i]: i for i in context_resource.entid2text}
    flush_at = 10
    flush_count = flush_at
    count = 0
    try:
        for idx, row in tqdm(pred_hr.iterrows()):
            if idx < start_count:
                continue
            h = row['head']
            r = row['rel']
            t = row['tail']
            if h in context_resource.entid2text and r in context_resource.relid2text:
                pred_text = [context_resource.entid2text[p] for p in t if p in context_resource.entid2text]
                prompt_t_template = f'''Rank candidates among [{'; '.join(pred_text[:10])}] based on the relevance to the query <{context_resource.entid2text[h]}, {context_resource.relid2text[r]}, ?>, with a score range of [0-1] where 1 the true. list result only.'''
                assistant_reply = rank_negs(prompt_t_template)
                negs = unwrap_reply(assistant_reply, text2id)
                if len(negs) > 0:
                    neg_list.append([h, r, negs])
                    flush_count -= 1
            if flush_count == 0:
                with open(out_file, 'a') as f:
                    for item in neg_list:
                        f.write(f"{str(item[0])}, {str(item[1])}\t{';'.join([str(neg_i) for neg_i in item[2]])}\n")
                    neg_list.clear()
                    flush_count = flush_at
                    count = idx
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        with open(out_file, 'a') as f:
            for item in neg_list:
                f.write(f"{str(item[0])}, {str(item[1])}\t{';'.join([str(neg_i) for neg_i in item[2]])}\n")
        count += len(neg_list)
        print(f"stopped at count {count}")


def generate_neg_candidates_tr(input_dir, out_file, start_count=0):
    # initialize context resource
    abox_file_path = input_dir + "abox_hrt_uri.txt"
    pred_file_path = input_dir + "correct_hrt.txt"
    context_resource = ContextResources(abox_file_path, class_and_op_file_path=input_dir,
                                        work_dir=input_dir)
    pred_df = read_hrt_2_hrt_int_df(pred_file_path)
    true_df = context_resource.hrt_to_scan_df
    pred_df = pd.concat([pred_df, true_df, true_df]).drop_duplicates(keep=False)
    # true_df_hr = true_df.groupby(['h', 'r'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    pred_hr = pred_df.groupby(['rel', 'tail'], group_keys=True, as_index=False).aggregate(lambda x: x.unique().tolist())
    context_resource.load_id2literal()
    neg_list = []
    text2id = {context_resource.entid2text[i]: i for i in context_resource.entid2text}
    flush_at = 10
    flush_count = flush_at
    count = 0
    try:
        for idx, row in tqdm(pred_hr.iterrows()):
            if idx < start_count:
                continue
            h = row['head']
            r = row['rel']
            t = row['tail']
            if t in context_resource.entid2text and r in context_resource.relid2text:
                pred_text = [context_resource.entid2text[p] for p in h if p in context_resource.entid2text]
                prompt_h_template = f'''Rank candidates among [{'; '.join(pred_text[:10])}] based on the relevance to the query <?, {context_resource.relid2text[r]}, {context_resource.entid2text[t]}>, with a score range of [0-1] where 1 the true. list result only.'''
                assistant_reply = rank_negs(prompt_h_template)
                negs = unwrap_reply(assistant_reply, text2id)
                if len(negs) > 0:
                    neg_list.append([negs, r, t])
                    flush_count -= 1
            if flush_count == 0:
                with open(out_file, 'a') as f:
                    for item in neg_list:
                        f.write(f"{str(item[2])}, {str(item[1])}\t{';'.join([str(neg_i) for neg_i in item[0]])}\n")
                    neg_list.clear()
                    flush_count = flush_at
                    count = idx
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        with open(out_file, 'a') as f:
            for item in neg_list:
                f.write(f"{str(item[2])}, {str(item[1])}\t{';'.join([str(neg_i) for neg_i in item[0]])}\n")
        count += len(neg_list)
        print(f"stopped at count {count}")


def unwrap_reply(reply, text2id):
    items = reply.split('\n')
    negs = []
    float_pattern = r"[0-1](\.)?[0-9]*"
    for i in items:
        candidates_score = i.split(' - ')
        candidate = candidates_score[0].split('.')[-1].strip()
        if candidate not in text2id:
            continue
        # Find all matches of the pattern in the input string
        float_search = re.search(float_pattern, candidates_score[-1].strip())
        if float_search is None:
            continue
        score = float(float_search.group())
        if score < 0.5:
            negs.append(text2id[candidate])
    return negs


def rank_negs(prompt):
    openai.api_key = ""
    msgs = [{"role": 'user', "content": prompt}]
    assistant_reply = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.8,
            timeout=5,
            messages=msgs)
        assistant_reply = response['choices'][0]['message']['content']
        return assistant_reply
    except Exception as e:
        print(f"An error occurred: {e}")
        return assistant_reply



if __name__ == '__main__':
    # generate_neg_candidates_hr("../resources/DB15K/", "../outputs/DB15K/pred_negs_hr.txt", 11602)
    generate_neg_candidates_tr("../resources/DB15K/", "../outputs/DB15K/pred_negs_tr.txt", 1045)
    # multi_request_generate_neg_candidates("../resources/DB15K/", "../outputs/DB15K/pred_negs_multi.txt", 0)
