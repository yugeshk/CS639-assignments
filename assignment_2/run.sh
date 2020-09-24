#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="source"

# Basic parsing of command line options
cfgOnly="n"
format="png"
while true; do
    case "$1" in 
        --cfg-only)
            cfgOnly="y"
            shift
            ;;
        --format)
            format=$2
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

if [[ $format != "png" && $format != "pdf" && $format != "jpg" ]]
then
    echo "CFG output format not supported"
    exit 1
fi

# Sanity Checks
if [[ "$#" -ne 1 ]]
then
    echo "Input file not provided"
    echo "Usage: bash run.sh <options> <input_file_name>"
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

if [[ ! `which dot` ]]
then
    echo "To generate and view dotfiles you need the GraphViz binaries installed."
    echo "For ubuntu, please run : sudo apt-get install graphviz"
    exit 1
fi

BASENAME="$(basename $1 .py)"
# Run Scripts
python3 "$BASE_DIR/$SRC_DIR/dump_astjson.py" $1 > "$BASE_DIR/$BASENAME.dump"
python3 "$BASE_DIR/$SRC_DIR/ast_to_tac.py" $1 "$BASE_DIR/$BASENAME.dump" "$BASE_DIR/$BASENAME.tac"
python3 "$BASE_DIR/$SRC_DIR/tac_to_cfgdotfile.py" "$BASE_DIR/$BASENAME.tac" "$BASE_DIR/$BASENAME.dot" "$BASE_DIR/$BASENAME.$format"

if [[ $cfgOnly == "y" ]]
then
    rm "$BASE_DIR/$BASENAME.dump" "$BASE_DIR/$BASENAME.tac" "$BASE_DIR/$BASENAME.dot"
fi