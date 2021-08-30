#!/usr/bin/env bash

export DIR_TMP="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$DIR_TMP
export PYTHONPATH=$PYTHONPATH:$DIR_TMP/abox_scanner
export PYTHONPATH=$PYTHONPATH:$DIR_TMP/openKE
export PYTHONPATH=$PYTHONPATH:$DIR_TMP/blp
export PYTHONPATH=$PYTHONPATH:$DIR_TMP/pipelines
export PYTHONPATH=$PYTHONPATH:$DIR_TMP/scripts
export PYTHONWARNINGS='ignore:semaphore_tracker:UserWarning'
echo PYTHONPATH=$PYTHONPATH