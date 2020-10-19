#!/bin/bash

find . | grep "_optimized.py" | grep -v "testcases" | xargs rm
