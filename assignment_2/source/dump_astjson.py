import sys
import os
import json
from ast import parse
try:
    from ast2json import ast2json
except ImportError:
    print("This script requires the python-pip package ast2json. Please install it or run setup_env.sh")

#Input file
input_python_file = sys.argv[1]

ast = ast2json(parse(open(input_python_file).read()))
print(json.dumps(ast,indent=4))
