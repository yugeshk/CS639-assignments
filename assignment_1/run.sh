#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="source"

if [[ ! -f $1 ]]
then
    echo "Input file does not exist!"
    exit 1
fi

python3 $BASE_DIR/$SRC_DIR/dump_astjson.py $1 > $BASE_DIR/$SRC_DIR/astjson.dump
python3 $BASE_DIR/$SRC_DIR/analyze_astjson.py $1 $BASE_DIR/$SRC_DIR/astjson.dump > analysis.output

echo "Result saved in analysis.output file"

rm $BASE_DIR/$SRC_DIR/astjson.dump