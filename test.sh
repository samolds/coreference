#!/bin/sh

RESPONSE_LIST='data/filelists/responselist.txt'
DATA_DIR='data/dev/'

if [[ $# -eq 1 ]]; then
  RESPONSE_LIST=$1
elif [[ $# -eq 2 ]]; then
  RESPONSE_LIST=$1
  DATA_DIR=$2
fi

source virtualenv/bin/activate
cd scorer && python new-coref-scorer.py ../$RESPONSE_LIST ../$DATA_DIR
deactivate
