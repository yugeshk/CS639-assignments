#!/bin/bash
set -euo pipefail

#TODO: add requirement for pip3, python3, etc

#Remove virtualenv if present
rm -rf venv

#Create virtualenv
python3 -m virtualenv venv
source scripts/venv.sh

#Install requirements
pip3 install -r requirements.txt