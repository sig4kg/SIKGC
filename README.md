# TREATKGC
1. Triple producer

There are three pipelines: E-method, R-method, L-method
```bash
source setup.sh
cd pipeline 
python pipeline_C_E_C.py
python pipeline_C_R_C.py

```

Data format: 
Triples: h, r and t, seperated by tab
Ontology: ontology in OWL, n-triples or ttl format, containing disjoint class, domain/range 

2. Consistency Checking:
Consistency checking is done by abox_scanner, it's already included in pipelines 
The TBox patterns are created by another project:  https://github.com/sylviawangfr/HermitTreat.git 