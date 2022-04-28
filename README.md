# TREATKGC
1. Triple producer


```bash
source setup.sh
cd ../../pipeline 
python experiments.py --dataset=TREAT --work_dir=../outputs/treat/ --loops=1 --pipeline="l" --use_gpu=True --rel_model=transe
```
2. TREAT downsteam sampling

```bash
source setup.sh
cd ../../pipeline 
python TREAT_downstream.py
```
There are a few output files in outputs/treat_downstream/: \
blp_new_triples.csv: all produced triples with scores. \
sample_and_score.pt: train sampling file, with format h,r,t,s. \
valid_hrt.txt: triples that consistent with schema. \
invalid_hrt.txt: triples that consistent with schema. 


3. Data format: 
Triples: h, r and t, seperated by tab
Ontology: ontology in OWL, n-triples or ttl format, containing disjoint class, domain/range 
The L-method need literals, please refer to resources/TREAT for data formats.
