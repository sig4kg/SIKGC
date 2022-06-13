import pandas as pd
from tqdm import tqdm
import file_util
import scripts.run_scripts


def get_uri_short(uri_long):
    delimiter = '#' if '#' in uri_long else '/'
    items = uri_long.rsplit(delimiter, 1)
    return items[0] + delimiter, items[1]

REL_RANGE = "<http://www.w3.org/2000/01/rdf-schema#range>"
REL_DOMAIN = "<http://www.w3.org/2000/01/rdf-schema#domain>"
REL_TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
TAIL_CLASS = "<http://www.w3.org/2002/07/owl#Class>"


# if no range for r, we create a new class for Range(r), and add entities type assertions into abox
def fix_domain_range(in_dir,  out_dir):
    scripts.run_scripts.delete_dir(out_dir)
    file_util.init_dir(out_dir)
    abox_file_hrt = in_dir + "abox_hrt_uri.txt"
    tbox_file_nt = in_dir + "tbox.nt"
    ent2type_file = in_dir + "entity2type.txt"
    ops_file = in_dir + "AllObjectProperties.txt"
    clz_file = in_dir + "AllClasses.txt"
    rel_hrt_df = pd.read_csv(
        abox_file_hrt, header=None, names=['head', 'rel', 'tail'], sep="\t")
    original_schema_hrt_df = pd.read_csv(
        tbox_file_nt, header=None, names=['head', 'rel', 'tail', 'dot'], sep=" ")
    schema_hrt_df = original_schema_hrt_df[['head', 'rel', 'tail']].dropna(how='any')
    with open(ops_file, mode='r') as f1:
        lines = f1.readlines()
        ops = [f"<{l.strip()}>" for l in lines]
    op_schema = schema_hrt_df.query("head in @ops").groupby('head', group_keys=True, as_index=False)
    r2range = dict()
    r2domain = dict()
    for g in tqdm(op_schema, desc="finding range domain to fix"):
        # for g in gp:
        r = g[0][1:-1]
        r_triples_df = g[1]
        any_range = r_triples_df.query("rel == @REL_RANGE")
        if len(any_range.index) == 0:
            prefix_str, r_str = get_uri_short(r)
            range_name = f"{prefix_str}Range_{r_str}"
            r2range.update({r: range_name})

        any_domain = r_triples_df.query("rel == @REL_DOMAIN")
        if len(any_domain.index) == 0:
            prefix_str, r_str = get_uri_short(r)
            domain_name = f"{prefix_str}Domain_{r_str}"
            r2domain.update({r: domain_name})

    ent2types = dict()
    for r in tqdm(r2range, desc="add range type to entities"):
        ent_tails = rel_hrt_df.query("rel == @r")['tail'].drop_duplicates(keep='first')
        for ent in ent_tails:
            if ent in ent2types:
                ent2types[ent].append(r2range[r])
            else:
                ent2types.update({ent: [r2range[r]]})
    for r in tqdm(r2domain, desc="add domain type to entities"):
        ent_heads = rel_hrt_df.query("rel == @r")['head'].drop_duplicates(keep='first')
        for ent in ent_heads:
            if ent in ent2types:
                ent2types[ent].append(r2domain[r])
            else:
                ent2types.update({ent: [r2domain[r]]})
    # extend tbox
    new_tbox_triples = pd.concat([range2triples(r2range), domain2triples(r2domain)])
    new_tbox_triples['dot'] = '.'
    extend_schema_hrt_df = pd.concat([original_schema_hrt_df, new_tbox_triples])
    extend_schema_hrt_df.to_csv(out_dir + "tbox.nt",  header=False, index=False, sep=' ')
    # extend entity2type.txt
    existing_ent2classes = dict()
    with open(ent2type_file, mode='r') as f:
        lines = f.readlines()
        for l in lines:
            items = l.strip().split('\t')
            if len(items) < 2:
                existing_ent2classes.update({items[0]: []})
            else:
                ent = items[0]
                classes = items[1].split(';')
                existing_ent2classes.update({ent: classes})
    for ent in ent2types:
        if ent in existing_ent2classes:
            existing_ent2classes[ent].extend([t for t in ent2types[ent]])
    file_util.save_list_to_file([f"{x}\t{';'.join(existing_ent2classes[x])}" for x in existing_ent2classes], out_dir + "entity2type.txt")
    # extend AllClasses.txt
    new_clz = list(r2range.values())
    new_clz.extend(list(r2domain.values()))
    with open(clz_file, mode='r') as f:
        lines = f.readlines()
        all_clz = [l.strip() for l in lines]
    all_clz.extend(new_clz)
    file_util.save_list_to_file(all_clz, out_dir + "AllClasses.txt")


def range2triples(r2range_dict) -> pd.DataFrame:
    tri_list = []
    for r in r2range_dict:
        tri_list.append([f"<{r}>", REL_RANGE, f"<{r2range_dict[r]}>"])
        tri_list.append([f"<{r2range_dict[r]}>", REL_TYPE, TAIL_CLASS])
    return pd.DataFrame(data=tri_list, columns=['head', 'rel', 'tail'])


def domain2triples(r2domain_dict) -> pd.DataFrame:
    tri_list = []
    for r in r2domain_dict:
        tri_list.append([f"<{r}>", REL_DOMAIN, f"<{r2domain_dict[r]}>"])
        tri_list.append([f"<{r2domain_dict[r]}>", REL_TYPE, TAIL_CLASS])
    return pd.DataFrame(data=tri_list, columns=['head', 'rel', 'tail'])


if __name__ == "__main__":
    fix_domain_range("../resources/TREAT/", "../outputs/fix_TREAT/")
    # fix_domain_range("../resources/NELL/", "../outputs/fix_NELL/")
    # fix_domain_range("../resources/DBpedia-politics/", "../outputs/fix_DBpedia/")

