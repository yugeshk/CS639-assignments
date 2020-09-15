#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="source"

# Sanity Checks
if [[ "$#" -ne 1 ]]
then
    echo "Input file not provided"
    echo "Usage: bash run.sh <input_file_name>"
fi

if [[ ! -f $1 ]]
then
    echo "Input file does not exist!"
    exit 1
fi

if [[ ! `which python3.8` ]]
then
    echo "Python3.8 not found. This utility is not supported for other versions of python."
    exit 1
fi

if [[ `pip3 freeze | grep ast2json | wc -l` -ne 1 ]]
then
    echo "ast2json python package not found. Please install."
    exit 1
fi

BASENAME="$(basename $1 .py)"

# Run Scripts
python3 "$BASE_DIR/$SRC_DIR/dump_astjson.py" $1 > "$BASE_DIR/$BASENAME.dump"
python3 "$BASE_DIR/$SRC_DIR/analyze_astjson.py" $1 "$BASE_DIR/$BASENAME.dump" > $BASENAME.output

echo "Result saved in $BASENAME.output file"
