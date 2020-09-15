#!/bin/bash

if [[ "$#" -eq 0 ]]
then
    rm *.dump
    rm *.output
fi

for ext in "$@"
do
    rm *.$ext
done