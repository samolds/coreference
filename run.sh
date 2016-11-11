#!/bin/sh

FILE_LIST='data/filelists/devFiles.txt'
RESPONSE_DIR='scorer/responses/'

if [[ $# -eq 1 ]]; then
  FILE_LIST=$1
elif [[ $# -eq 2 ]]; then
  FILE_LIST=$1
  RESPONSE_DIR=$2
fi

source virtualenv/bin/activate
python src/main.py $FILE_LIST $RESPONSE_DIR
deactivate
