#!/bin/sh

./getenv.sh
source virtual_env/bin/activate

pip install nltk

python src/coreference.py singleFile.txt data/scorer/responses 