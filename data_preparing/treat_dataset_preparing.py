def add_type_to_text(in_txt, in_type, out_txt):
    ent2text = dict()
    ent2type = dict()
    with open(in_txt, 'r') as f1:
        text_lines = f1.readlines()
        for t in text_lines:
            items = t.strip().split('\t')
            ent2text.update({items[0]: items[1]})
        f1.close()
    with open(in_type, 'r') as f2:
        type_lines = f2.readlines()
        for l in type_lines:
            items = l.strip().split('\t')
            ent2type.update({items[0]: items[1].split(';')})
        f2.close()
    uri12str = {"http://treat.net/onto.owl#Domain_category": "category domain",
                "http://treat.net/onto.owl#Range_category": "category range",
                "http://treat.net/onto.owl#IPV4": "IPV4",
                "http://treat.net/onto.owl#Domain_peer_up": "peer up with others"}
    for ent in ent2text:
        if ent in ent2type:
            for uri in ent2type[ent]:
                if uri in uri12str:
                    ent2text.update({ent: ent2text[ent] + ', ' + uri12str[uri]})
    with open(out_txt, 'w') as f3:
        for ent in ent2text:
            to_str = f"{ent}\t{ent2text[ent]}\n"
            f3.write(to_str)
        f3.close()

if __name__ == "__main__":
    add_type_to_text("../resources/TREAT/entity2text.txt",
                     "../resources/TREAT/entity2type.txt",
                     "../outputs/fix_TREAT/entity2text.txt")
