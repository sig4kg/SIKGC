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
[ ! -f "$WORK_DIR/HermitMaterialize-1.0-SNAPSHOT-jar-with-dependencies.jar" ] && cp ../scripts/HermitMaterialize-1.0-SNAPSHOT-jar-with-dependencies.jar $WORK_DIR/
echo "Materializing abox and tbox..."
java -Dontology=tbox_abox.nt -Doutput_dir=./ -jar $WORK_DIR/HermitMaterialize-1.0-SNAPSHOT-jar-with-dependencies.jar
echo "Done with Materialization."