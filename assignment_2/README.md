## REPORT : 

### Implementation Details:

We dumped the json corresponding to a file created using ast to json. After that we read the json using the json library. We wrote a function that recursively reads a json object called visit_node, which takes as input a node and recursively visits it's children.
    
On the basis of the "type" field of each node we wrote different functions to handle different types of node. For instance, if we encounter a node of type For, we get the it's children corresponding to "target" and "iter" fields which give us the loop variables, and the object being iterated over. 
    
Using the lineno, col_offset, end_lineno, and end_col_offset fields of these nodes, we get the text corresponding to these constructs, and store that text. After we are done with the whole json object we print the text that was accumulated. 

### How to build and run:

To run this utility, you must have `python3.8`, `pip3.8`, `ast2json` and `pydotplus` python packages and `Graphviz` binaries installed . Scripts will complain if these are not present.
This utility contains a script `setup_env.sh` that will setup a virtualenv and install necessary python packages (incase you want to use a virtualenv). To setup the virtualenv do:

    ./setup_env.sh
    source venv/bin/activate

To run this utility simply run the following command in the base directory:

    ./run.sh <options> <input_python_file>

The `run.sh` script supports the following command-line options:

    --cfg-only : This generates only the cfg file (png by default) and removes all intermidiate files generated
    --format (png|pdf|jpg) : Three output file formats are supported. This flag can be used to specify the output format

Since the command line option parsing is rudamentary, script might complain or not work properly if the options are provided incorrectly. Options must be provided before the input file and there should be a bash-space between `--format` and `png|pdf|jpg`.

This script will generate four files `<input_python_file>.dump`, `<input_python_file>.tac`, `<input_python_file>.dot` and `<input_python_file>.(cfg)` in the directory from which `run.sh` was executed.

To clean the base directory, simply run:

    ./clean.sh

This will remove all `*.dump`, `*.tac`, `*.dot`, `*.png`, `*.pdf` and `*.jpg` files. You can selectively also clean files of certain extensions (e.g., dump) by doing:

    ./clean.sh dump


    