#!/bin/sh

# Select current version of virtualenv:
VERSION=15.0.0
# Name your first "bootstrap" environment:
INITIAL_ENV=virtualenv
# Set to whatever python interpreter you want for your first environment:
PYTHON=$(which python)
URL_BASE=https://pypi.python.org/packages/source/v/virtualenv

# --- Real work starts here ---
curl -O $URL_BASE/virtualenv-$VERSION.tar.gz
tar xzf virtualenv-$VERSION.tar.gz
# Create the first "bootstrap" environment.
$PYTHON virtualenv-$VERSION/virtualenv.py $INITIAL_ENV
# Install virtualenv into the environment.
$INITIAL_ENV/bin/pip install virtualenv-$VERSION.tar.gz

# Don't need this anymore.
rm -rf virtualenv-$VERSION
rm -rf virtualenv-$VERSION.tar.gz


# download nltk and dependencies
source $INITIAL_ENV/bin/activate
pip install nltk
pip install numpy
deactivate
