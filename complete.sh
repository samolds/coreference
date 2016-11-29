#!/bin/sh

# run setup.sh if it hasn't already been run
if [[ ! -d "virtualenv" ]]; then
  ./setup.sh
fi

# default to running dev dataset
DATA_SET='dev'
if [[ $# -eq 1 ]]; then
  DATA_SET=$1
fi

if [[ "$DATA_SET" = "dev" ]]; then
  ./run.sh data/filelists/devFiles.txt scorer/responses/
  ./test.sh data/filelists/responselist.txt data/dev/
elif [[ "$DATA_SET" = "singledev" ]]; then
  ./run.sh data/filelists/singleFile.txt scorer/responses/
  ./test.sh data/filelists/responselist.txt data/dev/
elif [[ "$DATA_SET" = "singletest1" ]]; then
  ./run.sh data/filelists/singleFile.txt scorer/responses/
  ./test.sh data/filelists/responselist.txt data/test1/
elif [[ "$DATA_SET" = "test1" ]]; then
  ./run.sh data/filelists/test1Files.txt scorer/responses/
  ./test.sh data/filelists/responselist.txt data/test1/
fi;
