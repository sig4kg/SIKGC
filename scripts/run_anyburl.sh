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

if [ ! -d "$WORK_DIR/rules" ];then
  mkdir "$WORK_DIR/rules"
else
  echo "$WORK_DIR/rules" exist
fi

if [ ! -d "$WORK_DIR/predictions" ];then
  mkdir "$WORK_DIR/predictions"
else
  echo "$WORK_DIR/predictions" exist
fi


[ ! -f "$WORK_DIR/AnyBURL-JUNO.jar" ] && cp ../scripts/AnyBURL-JUNO.jar $WORK_DIR/
echo "Learning horn rule via AnyBURLs..."
java -Xmx3G -cp $WORK_DIR/AnyBURL-JUNO.jar de.unima.ki.anyburl.LearnReinforced $WORK_DIR/config-learn.properties
# the following cmds are not executed after last cmd exits from multi-threads
#echo "Learning new triples..."
#java -Xmx3G -cp $WORK_DIR/AnyBURL-JUNO.jar de.unima.ki.anyburl.Apply $WORK_DIR/config-apply.properties
#echo "Evaluating AnyBURL..."
#java -Xmx3G -cp $WORK_DIR/AnyBURL-JUNO.jar de.unima.ki.anyburl.Eval $WORK_DIR/config-eval.properties
#echo "Done with AnyBURL."