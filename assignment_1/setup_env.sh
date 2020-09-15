#!/bin/bash
set -euo pipefail

#TODO: add requirement for pip3, python3, etc
if [[ ! `which python3.8` ]]
then
    echo "Python 3.8 not found. This utility does not support over python versions."
    exit 1
fi

if [[ ! `which pip3` ]]
then
    echo "pip 3 not found. This utility does not support over python versions."
    exit 1
fi

#Install virtualenv if not present
if [[ `pip3 freeze | grep virtualenv | wc -l` -ne 1 ]]
then
    pip3 install --user virtualenv
fi

#Remove virtualenv if present
rm -rf venv

#Create virtualenv
python3.8 -m virtualenv venv
source scripts/venv.sh

#Install requirements
pip3 install -r requirements.txt