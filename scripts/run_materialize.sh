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
if [ -f "$WORK_DIR/tbox_dllite.ttl" ];then
  java -Xmx15G -Dtask=Materialize -Dschema=tbox_dllite.ttl -Dabox=abox.nt -Doutput_dir=./ -jar $WORK_DIR/TBoxTREAT-1.0.jar
else
  java -Xmx15G -Dtask=Materialize -Dschema=tbox.nt -Dabox=abox.nt -Doutput_dir=./ -jar $WORK_DIR/TBoxTREAT-1.0.jar
fi
echo "Done with Materialization."