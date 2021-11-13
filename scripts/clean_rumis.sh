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

if [ -d "$WORK_DIR/DLV" ];then
    mv $WORK_DIR/DLV $LAST_ROUND
fi
[ -f "$WORK_DIR/ideal.data.txt" ] && mv $WORK_DIR/ideal.data.txt $LAST_ROUND
[ -f "$WORK_DIR/training.data.txt" ] && mv $WORK_DIR/train.data.txt $LAST_ROUND
[ -f "$WORK_DIR/experiment.txt" ] && mv $WORK_DIR/experiment.txt $LAST_ROUND
[ -f "$WORK_DIR/encode.txt" ] && mv $WORK_DIR/encode.txt $LAST_ROUND
[ -f "$WORK_DIR/invalid_hrt.txt" ] && mv $WORK_DIR/invalid_hrt.txt $LAST_ROUND
[ -f "$WORK_DIR/valid_hrt.txt" ] && mv $WORK_DIR/valid_hrt.txt $LAST_ROUND
[ -f "$WORK_DIR/horn-rules.txt" ] && mv $WORK_DIR/horn-rules.txt $LAST_ROUND
[ -f "$WORK_DIR/horn-rules-stats.txt" ] && mv $WORK_DIR/horn-rules-stats.txt $LAST_ROUND
[ -f "$WORK_DIR/revised-rules.txt" ] && mv $WORK_DIR/revised-rules.txt $LAST_ROUND

