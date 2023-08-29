# SICKLE
1. Data
- We used three datasets: DBped-P, DB15K, and NELL. 
- Unzip resources/NELL.zip to resources/NELL/
- Unzip resources/DB15K.zip to resources/DB15K/

Data format:
- Triples: filename abox_hrt_uri.txt, h, r and t, seperated by tab
- Ontology: ontology in OWL, n-triples or ttl format, containing disjoint class, domain/range
- The L-method need literals, please refer to resources/NELL for data formats.

2. Dependencies
- Install pytorch according to your cpu/gpu environment.
- Install all packages in requirements.txt. Feel free to use conda, pyenv or others.
- Install java, jdk, maven
3. Preparing Konclude reasoner
```bash
mkdir java_owlapi/Konclude
unzip resources/packages/Konclude-v0.7.0-1135-Linux-x64-GCC-Static-Qt5.12.10.zip -d java_owlapi
mv java_owlapi/Konclude-v0.7.0-1135-Linux-x64-GCC-Static-Qt5.12.10 java_owlapi/Konclude 
```
4. Preparing TBox scanner
```bash
cd java_owlapi/TBoxTREAT
mvn clean install
```

5. Triple producer
```bash
source setup.sh
cd pipeline
python experiments.py --dataset=DB15K --work_dir="../outputs/proDB15K/"  --produce=True --silver_eval=False --pred_type=False --pipeline=a_m_l --loops=2 --rel_model=complex --inductive=False --parallel=True --schema_aware_sampling=False 
```
"a_m_l" means run [AnyBURL](https://web.informatik.uni-mannheim.de/AnyBURL/), materialization, [blp](https://github.com/dfdazac/blp) together. If you only run single method, just use option a, m or l.
--inductive=True would set blp to literal embedding. --inductive=False would set blp to pure KG embedding. Please refer to [blp paper](https://arxiv.org/abs/2010.03496) for more information.

For type prediction:
- Set --pred_type=True. This will run type prediction after the link prediction step.
- Or run 
```bash
cd module_utils
python type_producer.py --dataset=DB15K --work_dir="../outputs/proDB15K/a_m_l/
```
6. For custom datasets:
- Please refer to the required data format.
- You need to generate TBox inconsistency justification patterns before you run the pipeline:
```
scripts/tbox_Scanner.sh  schema_file work_dir
```
----------------------------------------------

7. TREAT downsteam sampling (For my co-worker's project. You don't need this)

```bash
source setup.sh
cd ../../pipeline 
python TREAT_downstream.py
```
There are a few output files in outputs/treat_downstream/: \
- blp_new_triples.csv: all produced triples with scores. 
- sample_and_score.pt: train sampling file, with format h,r,t,s. 
- valid_hrt.txt: triples that consistent with schema. 
- invalid_hrt.txt: triples that consistent with schema. 
The entities and relations in these files are indexed by abox_scanner/abox_utils.py. However, it can be translated to URI with minor changes in a pipeline.



