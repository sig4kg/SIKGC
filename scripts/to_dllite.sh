#!/usr/bin/env bash
if [[ $# -ne 2 ]]; then
    echo Usage: bash $0 SCHEMA_FILE WORK_DIR
    exit 1
fi

set -e

# CLI args
SCHEMA_FILE=$1
WORK_DIR=$2

if [ ! -d "$WORK_DIR" ];then
  mkdir "$WORK_DIR"
else
  echo "$WORK_DIR" exist
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

echo "Materializing abox and tbox..."
java -Dtask=DL-lite -Dschema=$SCHEMA_FILE -Doutput_dir=./ -jar $WORK_DIR/TBoxTREAT-1.0.jar
echo "Done with Materialization."