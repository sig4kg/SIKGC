#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    echo Usage: bash $0 WORK_DIR
    exit 1
fi

set -e

# CLI args
WORK_DIR=$1
LAST_ROUND=$WORK_DIR/last_round

if [ ! -d "$WORK_DIR" ];then
  exit 0
fi

if [ ! -d "$LAST_ROUND" ];then
  mkdir "$LAST_ROUND"
fi

mv $WORK_DIR/*.txt $LAST_ROUND
mv $WORK_DIR/train/train2id.txt $LAST_ROUND
mv $WORK_DIR/checkpoint/transe.ckp $LAST_ROUND
