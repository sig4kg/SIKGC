#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    echo Usage: bash $0 WORK_DIR
    exit 1
fi

set -e

# CLI args
WORK_DIR=$1
LAST_ROUND=$WORK_DIR/last_round

if [ ! -d "$LAST_ROUND" ];then
  mkdir "$LAST_ROUND"
fi

[ -d "$WORK_DIR/predictions" ] && mv $WORK_DIR/predictions/* $LAST_ROUND
[ -d "$WORK_DIR/rules" ] && mv $WORK_DIR/rules $LAST_ROUND
[ -f "$WORK_DIR/invalid_hrt.txt" ] && mv $WORK_DIR/invalid_hrt.txt $LAST_ROUND
[ -f "$WORK_DIR/valid_hrt.txt" ] && mv $WORK_DIR/valid_hrt.txt $LAST_ROUND
[ -f "$WORK_DIR/all_triples.txt" ] && mv $WORK_DIR/all_triples.txt $LAST_ROUND
[ -f "$WORK_DIR/test*.txt" ] && mv $WORK_DIR/test*.txt $LAST_ROUND
[ -f "$WORK_DIR/config-apply.properties" ] && mv $WORK_DIR/config-apply.properties $LAST_ROUND

