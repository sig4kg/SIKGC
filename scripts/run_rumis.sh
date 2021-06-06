#!/usr/bin/env bash
if [[ $# -ne 1 ]]; then
    echo Usage: bash $0 WORK_DIR
    exit 1
fi

set -e

# CLI args
WORK_DIR=$1

if [ ! -d "$WORK_DIR" ];then
  mkdir "$WORK_DIR"
else
  echo "$WORK_DIR" exist
fi


[ ! -f "$WORK_DIR/rumis-1.0.jar" ] && cp ../scripts/rumis-1.0.jar $WORK_DIR/
[ ! -f "$WORK_DIR/dlv.bin" ] && cp ../scripts/dlv.bin $WORK_DIR/
echo "learning horn rule..."
java -jar $WORK_DIR/rumis-1.0.jar -e=pos -l=$WORK_DIR/ideal.data.txt
echo "learning nonmonotonic rule..."
java -jar $WORK_DIR/rumis-1.0.jar -e=neg -p=horn-rules.txt -l=$WORK_DIR/ideal.data.txt -r=2 -t=10
echo "Spliting train data..."
java -jar $WORK_DIR/rumis-1.0.jar -e=new -l=$WORK_DIR/ideal.data.txt -o=0.9 1>$WORK_DIR/training.data.txt
[ -f "horn-rules.txt" ] && mv horn-rules.txt $WORK_DIR/
[ -f "horn-rules-stats.txt" ] && mv horn-rules-stats.txt $WORK_DIR/
[ -f "revised-rules.txt" ] && mv revised-rules.txt $WORK_DIR/
echo "Learning new triples..."
java -jar $WORK_DIR/rumis-1.0.jar -e=exp -f=$WORK_DIR -r=2 -t=10 -d -s 1>$WORK_DIR/experiment.txt
echo "Done with Rumis."