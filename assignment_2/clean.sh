#!/bin/bash

if [[ "$#" -eq 0 ]]
then
    rm -f *.dump
    rm -f *.tac
    rm -f *.dot
    rm -f *.png
    rm -f *.pdf
    rm -f *.jpg
fi

for ext in "$@"
do
    rm -f *.$ext
done