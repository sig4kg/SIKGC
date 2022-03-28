
from abox_scanner.ContextResources import ContextResources


class PatternTypeDiscjointness():
    def __init__(self, context_resources: ContextResources) -> None:
        self._pattern_dict = None
        self._context_resources = context_resources

    def scan_pattern_df_rel(self, output_dir):
        invalid = {}
        valid = {}
        ent2types = self._context_resources.entid2classids
        for ent in ent2types:
            ent_types = ent2types[ent]
            is_valid = True
            for t in ent_types:
                if t not in self._context_resources.entid2classids or t not in self._pattern_dict:
                    continue
                disjoint_class = self._pattern_dict[t]
                if any([ent_t in disjoint_class for ent_t in ent_types]):
                    invalid.update({ent: ent2types[ent]})
                    is_valid = False
                    break
            if is_valid:
                valid.update({ent: ent2types[ent]})
        with open(output_dir + "valid_type.txt", encoding='utf-8', mode='w') as out_f:
            for ent in valid:
                out_f.write(f"{self._context_resources.id2ent[ent]}\t{';'.join([self._context_resources.classid2class[i] for i in valid[ent] if i in self._context_resources.classid2class])}\n")
        with open(output_dir + "invalid_type.txt", encoding='utf-8', mode='w') as out_f:
            for ent in invalid:
                out_f.write(f"{self._context_resources.id2ent[ent]}\t{';'.join([self._context_resources.classid2class[i] for i in invalid[ent] if i in self._context_resources.classid2class])}\n")

    def pattern_to_int(self, entry: str):
        with open(entry) as f:
            pattern_dict = dict()
            lines = f.readlines()
            for l in lines:
                items = l.strip().split('\t')
                r1_uri = items[0][1:-1]
                if r1_uri not in self._context_resources.class2id:
                    continue
                r1 = self._context_resources.class2id[r1_uri]
                r2_l = items[1].split('@@')
                r2 = [self._context_resources.class2id[rr2[1:-1]] for rr2 in r2_l if rr2[1:-1] in self._context_resources.class2id]
                if len(r2) > 0:
                    pattern_dict.update({r1: r2})
            self._pattern_dict = pattern_dict