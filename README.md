# TREATKGC
1. Triple producer

There are three pipelines: E-method, R-method, L-method
```bash
source setup.sh
cd OpenKE/openke
bash make.sh
cd ../../pipeline 
python pipeline_C_E_C.py
python pipeline_C_R_C.py

```

Data format: 
Triples: h, r and t, seperated by tab
Ontology: ontology in OWL, n-triples or ttl format, containing disjoint class, domain/range 
The L-method need literals, please refer to resources/umls2 for data formats.
