import pandas as pd
from tqdm import tqdm
import file_util
from abox_scanner.AboxScannerScheduler import AboxScannerScheduler
from abox_scanner.ContextResources import ContextResources


def filling_type(in_dir, out_dir):
    triples_path = in_dir + "abox_hrt_uri.txt"  # h, t, r
    tbox_patterns_path = in_dir + "tbox_patterns/"
    context_res = ContextResources(triples_path, class_and_op_file_path=in_dir, work_dir=out_dir)
    abox_scanner_scheduler = AboxScannerScheduler(tbox_patterns_path, context_resources=context_res)
    abox_scanner_scheduler.register_patterns_all()
    backup_to_scan_df = context_res.hrt_to_scan_df.copy(deep=True)
    v, inv = abox_scanner_scheduler.scan_rel_IJPs(out_dir, False)
    corrs, incorr = abox_scanner_scheduler.scan_schema_correct_patterns(out_dir, False)
    lack_of_type_df = pd.concat([incorr, inv]).drop_duplicates(keep=False)
    to_fill = lack_of_type_df.groupby('rel', group_keys=True, as_index=False)
    r2domain = abox_scanner_scheduler.get_schema_correct_strategy_patterns("PatternPosDomain")
    r2range = abox_scanner_scheduler.get_schema_correct_strategy_patterns("PatternPosRange")
    for g in tqdm(to_fill, desc="finding range domain to fix"):
        r = g[0]
        r_triples_df = g[1]
        r_D = r2domain[r] if r in r2domain else []
        r_R = r2range[r] if r in r2range else []
        if len(r_D) > 0:
            r_heads = r_triples_df['head'].drop_duplicates(keep='first')
            for ent in r_heads:
                ent_types = context_res.entid2classids[ent] if ent in context_res.entid2classids else []
                if any([et in r_D for et in ent_types]):
                    continue
                ent_types.append(r_D[0])
                if ent in context_res.entid2classids:
                    for te in ent_types:
                        if te not in context_res.entid2classids[ent]:
                            context_res.entid2classids[ent].append(te)
                else:
                    context_res.entid2classids.update({ent: ent_types})
        if len(r_R) > 0:
            r_tails = r_triples_df['tail'].drop_duplicates(keep='first')
            for ent in r_tails:
                ent_types = context_res.entid2classids[ent] if ent in context_res.entid2classids else []
                if any([et in r_R for et in ent_types]):
                    continue
                ent_types.append(r_D[0])
                if ent in context_res.entid2classids:
                    for te in ent_types:
                        if te not in context_res.entid2classids[ent]:
                            context_res.entid2classids[ent].append(te)
                else:
                    context_res.entid2classids.update({ent: ent_types})

    # context_res.hrt_int_df = v
    # context_res.to_ntriples(out_dir, in_dir + "tbox.nt")
    # check schema-correctness again
    context_res.hrt_to_scan_df = v
    context_res.hrt_int_df = None
    v2, inv2 = abox_scanner_scheduler.scan_rel_IJPs(out_dir, False)
    c2, inc2 = abox_scanner_scheduler.scan_schema_correct_patterns(out_dir, True)

    write_str = []
    for ent in context_res.entid2classids:
        ent_str = context_res.id2ent[ent]
        ent_types = [context_res.classid2class[t] for t in context_res.entid2classids[ent]]
        to_str = f"{ent_str}\t{';'.join(ent_types)}"
        write_str.append(to_str)
    file_util.save_list_to_file(write_str, out_dir + "entity2type.txt", mode='w')


if __name__ == "__main__":
    # filling_type("../resources/TREAT/", "../outputs/fix_TREAT/")
    filling_type("../resources/NELL/", "../outputs/fix_NELL/")




