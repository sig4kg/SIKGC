#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    echo Usage: bash $0 WORK_DIR
    exit 1
fi

set -e

# CLI args
WORK_DIR=$1
LAST_ROUND=$WORK_DIR/last_round/

if [ ! -d "$WORK_DIR" ];then
  exit 0
fi

if [ ! -d "$LAST_ROUND" ];then
  mkdir "$LAST_ROUND"
fi

#[ -f "$WORK_DIR/entities.txt" ] && mv $WORK_DIR/entities.txt $LAST_ROUND
#[ -f "$WORK_DIR/relations.txt" ] && mv $WORK_DIR/relations.txt $LAST_ROUND
#[ -f "$WORK_DIR/valid_hrt.txt" ] && mv $WORK_DIR/valid_hrt.txt $LAST_ROUND
#[ -f "$WORK_DIR/invalid_hrt.txt" ] && mv $WORK_DIR/invalid_hrt.txt $LAST_ROUND
#[ -f "$WORK_DIR/dev-ents.txt" ] && mv $WORK_DIR/dev-ents.txt $LAST_ROUND
#[ -f "$WORK_DIR/train-ents.txt" ] && mv $WORK_DIR/train-ents.txt $LAST_ROUND
#[ -f "$WORK_DIR/test-ents.txt" ] && mv $WORK_DIR/test-ents.txt $LAST_ROUND
[ -f "$WORK_DIR/ind-dev.tsv" ] && mv $WORK_DIR/ind-dev.tsv $LAST_ROUND
[ -f "$WORK_DIR/ind-train.tsv" ] && mv $WORK_DIR/ind-train.tsv $LAST_ROUND
[ -f "$WORK_DIR/ind-test.tsv" ] && mv $WORK_DIR/ind-test.tsv $LAST_ROUND
[ -f "$WORK_DIR/all_triples.tsv" ] && mv $WORK_DIR/all_triples.tsv $LAST_ROUND
#[ -f "$WORK_DIR/checkpoint/transe.ckpt" ] && mv $WORK_DIR/checkpoint/transe.ckpt $LAST_ROUND
[ -f "$WORK_DIR/blp_new_triples.csv" ] && mv $WORK_DIR/blp_new_triples.csv $LAST_ROUND
