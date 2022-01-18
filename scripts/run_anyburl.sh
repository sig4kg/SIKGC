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

if [ ! -d "$WORK_DIR/anyburl" ];then
  mkdir "$WORK_DIR/anyburl"
else
  echo "$WORK_DIR/anyburl" exist
fi

if [ ! -d "$WORK_DIR/anyburl/predictions" ];then
  mkdir "$WORK_DIR/anyburl/predictions"
else
  echo "$WORK_DIR/anyburl/predictions" exist
fi


[ ! -f "$WORK_DIR/anyburl/AnyBURL-JUNO.jar" ] && cp ../scripts/AnyBURL-JUNO.jar $WORK_DIR/anyburl/
echo "learning horn rule via AnyBURLs..."
java -Xmx3G -cp $WORK_DIR/anyburl/AnyBURL-JUNO.jar de.unima.ki.anyburl.LearnReinforced $WORK_DIR/anyburl/config-learn.properties
echo "evaluating AnyBURL..."
java -Xmx3G -cp $WORK_DIR/anyburl/AnyBURL-JUNO.jar de.unima.ki.anyburl.Eval $WORK_DIR/anyburl/config-eval.properties
echo "Learning new triples..."
java -Xmx3G -cp $WORK_DIR/anyburl/AnyBURL-JUNO.jar de.unima.ki.anyburl.Apply $WORK_DIR/anyburl/config-apply.properties
echo "Done with AnyBURL."