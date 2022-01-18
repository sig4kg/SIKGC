#!/usr/bin/env bash
if [[ $# -ne 2 ]]; then
    echo Usage: bash $0 SCHEMA_FILE $1 WORK_DIR
    exit 1
fi

set -e

# CLI args
WORK_DIR=$2
SCHEMA_FILE=$1

echo "WORK_DIR: $WORK_DIR"
echo "SCHEMA_FILE: $SCHEMA_FILE"

if [ ! -d "$WORK_DIR" ];then
  mkdir "$WORK_DIR"
else
  echo "$WORK_DIR" exist
fi

if [ ! -d "$WORK_DIR/tbox_patterns/" ];then
  mkdir "$WORK_DIR/tbox_patterns"
fi

if [ ! -f "$WORK_DIR/TBoxTREAT-1.0.jar" ];then
  if [ ! -f "../java_owlapi/TBoxTREAT/target/TBoxTREAT-1.0.jar" ];then
    dir=$(pwd)
    cd ../java_owlapi/TBoxTREAT
    mvn clean install
    cd $dir
  fi
  cp ../java_owlapi/TBoxTREAT/target/TBoxTREAT-1.0.jar $WORK_DIR/
fi

if [ -f "$SCHEMA_FILE" ];then
  cp $SCHEMA_FILE $WORK_DIR/original_tbox.tmp
fi

echo "Computing TBox scanner patterns..."
java -Dtask=TBoxScanner -Dschema=original_tbox.tmp -Doutput_dir=./tbox_patterns/ -jar $WORK_DIR/TBoxTREAT-1.0.jar
java -Dtask=AllClass -Dschema=original_tbox.tmp -Doutput_dir=./ -jar $WORK_DIR/TBoxTREAT-1.0.jar
echo "Done with Computing TBox scanner patterns."