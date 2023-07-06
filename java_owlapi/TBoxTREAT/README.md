1. Install java, jdk, maven
2. build jar file
```bash
mvn clean install
```
3. Usage
- To convert OWL to DL-Lite
```bash
java -Dtask=DL-lite -Dschema=$SCHEMA_FILE -Doutput_dir=$OUTDIR -jar target/TBoxTREAT-1.0.jar
```
- To generate IJPs 
```bash
java -Dtask=TBoxScanner -Dschema=$SCHEMA_FILE -Doutput_dir=$OUTDIR -jar target/TBoxTREAT-1.0.jar
java -Dtask=AllClass -Dschema=$SCHEMA_FILE -Doutput_dir=$OUTDIR -jar target/TBoxTREAT-1.0.jar
```
- To materialise with Konclude
```bash
java -DkoncludeBinary=$path_to_koncludeBinary -Dtask=Konclude -Dschema=$SCHEMA_FILE -Dsparqls=role_queries.sparql -Doutput_dir=$OUTDIR  -jar target/TBoxTREAT-1.0.jar
```
- To materialise with TrOWL
```bash
java -Dtask=TrOWL -Dschema=$SCHEMA_FILE -Doutput_dir=$OUTDIR -jar target/TBoxTREAT-1.0.jar
```
4. Please check Main.java for other usages
