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


[ -f "$WORK_DIR/abox.nt" ] && mv $WORK_DIR/abox.nt $LAST_ROUND
[ -f "$WORK_DIR/tbox_abox.nt" ] && mv $WORK_DIR/tbox_abox.nt $LAST_ROUND
[ -f "$WORK_DIR/materialized_tbox_abox.owl" ] && mv $WORK_DIR/materialized_tbox_abox.owl $LAST_ROUND
[ -f "$WORK_DIR/materialized_tbox_abox.nt" ] && mv $WORK_DIR/materialized_tbox_abox.nt $LAST_ROUND
[ -f "$WORK_DIR/materialized_abox.nt" ] && mv $WORK_DIR/materialized_abox.nt $LAST_ROUND
[ -f "$WORK_DIR/tmp_*.xml" ] && rm $WORK_DIR/tmp_*.xml


