#!/bin/sh

./getenv.sh
source virtual_env/bin/activate

pip install nltk


python src/coreference.py allFiles.txt data/scorer/responses 