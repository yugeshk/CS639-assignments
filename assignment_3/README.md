## REPORT : 

### Implementation Details:

#### Construction of CFG:
    
1.  Owing to the nature of the problem statemnt we could not lower the source program to 3AC (or any other IR), as in *Assignment 2*, and make a CFG for it. This is because we needed to maintain a mapping of assignment statments in the graph to the corresponding nodes in the CFG so that we could tag them as dead/alive and re-create an optimized file in the source language. Morever, running an analysis on lowered IR would involve lifting it back to the source language. Therefore, we created a CFG directly from the AST using the class `GraphGenerator` in `graph_creation.py`. After this we need to define kill and gen for each statement.

2. We refer to the analysis given in the book, <https://dl.acm.org/doi/book/10.5555/1592955> and tune it slightly to fit our purpose (specifically, add support for function calls). 

3. After the faint variable analysis is complete and we have the set of faint variables at each program point, we remove the assignments to faint variables provided that their RHS does not have a function call(explained in limitations below) by tagging them as dead and then traverse the AST again, without printing the assignment nodes marked as dead.

#### Limitations

1. We conservatively avoid eliminating any Assignment statements that have `function_calls` in their RHS. This is because function calls may have side effects, e.g., it may print variables. One alternative (in `python--`) was to do the following (assuming `a` is faint in this case):

        a = b + foo(c,d)
    
    gets optimized to :

        b + foo(c,d)

but we decide against doing it because that would violate `python--` grammar (`python--` contain only *assignment statements*, *if-then*, *if-then-else*, *while loops* and *function calls*, but removing the assignment would reduce it to an *expression*).

2. Our Faint Variable Optimization may leave empty comditional or loop blocks that look like this:

        while:
            pass
        
        if:
            pass
        else:
            pass

We leave these blocks intentionally, since we acknowledge that optimizing these blocks away is not part of a **Faint Varible Optimization** pass. Moreover, the requirement in the problem statement was to:

> Identify all the statements that assign to a faint variable, and remove such assignments to generate an optimized program.

Therefore, we limit ourselves to optimizing faint assignment statements only. However, we note that removing such blocks in an additional optimization pass is not a huge challenge.

#### Constraints on Input

Running the optimizer on a file that contains constructs not part of the `python--` grammar will cause the tool to complain. Since the grammar does not support function definitions in particular, no source file that tries to use user-defined functions will work. Python inbuilts (or function that can be used without the need for a definition) are fine though.

### How to build and run:

To run the optimizer, you must have `python3.8`, `pip3.8` and `ast2json`. Scripts will complain if these are not present.
This utility contains a script `setup_env.sh` that will setup a virtualenv and install necessary python packages (incase you want to use a virtualenv). To setup the virtualenv do:

    ./setup_env.sh
    source venv/bin/activate

To run this utility simply run the following command in the base directory:

    ./run.sh <input_python_file>

This script will generate a file `<input_python_file>_optimized.py`

To clean the base directory, simply run:

    ./clean.sh

This will remove all optimized source files that follow the naming convention `<filename>_optimized.py` in the directory.


    
