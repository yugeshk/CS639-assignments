"""
Converts a Three-Address-Code file to CFG and outputs as .dot and .png (or other format as specified)
Usage : python tac_to_cfgdotfile.py <filename>.tac <filename>.dot <filename>.png (or .pdf etc)
Supported formats : png, 
"""

import sys
import os
import pydotplus
from subprocess import check_call
from program import Program
import re

#Global variables
tac_filename = sys.argv[1]
dot_filename = sys.argv[2]
cfg_filename = sys.argv[3]

def optimise_cfg(cfg):
    """Graphviz level graph optimisations"""


def escape_string(inp_string):
    """Helper function to escape characters for the DOT language"""

    return inp_string.translate(str.maketrans({'"': r'\"', "&": r"\&", "<": r"\<", ">": r"\>"}))

def add_tac_BasicBlocks(cfg, tac_BBlist):
    for b in tac_BBlist:
        b_id = tac_BBlist.index(b)
        node_attrs = {}
        node_attrs['shape'] = 'record'
        instr_list = b.get_text().split('\n')
        label_attr = '"{'+str(b_id)+':\\l'
        for i in instr_list:
            if i == '':
                continue
            if re.match(r'^(L[0-9]+:)', i):
                groups = re.search(r'^(L[0-9]+:)(.*)', i)
                tac_label = groups[1]
                rem_instr = groups[2]
                label_attr += ' ' + tac_label + '\\l'
                if rem_instr != '':
                    label_attr += '  ' + rem_instr + '\\l'
            else:
                label_attr += '  ' + escape_string(i) + '\\l'
        label_attr += '}"'
        node_attrs['label'] = label_attr
        graphviz_node = pydotplus.graphviz.Node(name='{}'.format(b_id), **node_attrs)
        cfg.add_node(graphviz_node)


def add_tac_edges(cfg, tac_edgelist):
    for e in tac_edgelist:
        graphviz_edge = pydotplus.graphviz.Edge(src='{}'.format(e[0]), dst='{}'.format(e[1]))
        cfg.add_edge(graphviz_edge)

if __name__ == "__main__":

    #Initialize Graphviz CFG object
    cfg_attrs = {'label': 'CFG for {}'.format(os.path.basename(tac_filename))}
    cfg = pydotplus.graphviz.Graph(graph_name="CFG for {}".format(tac_filename), graph_type='digraph', **cfg_attrs)

    with open(tac_filename, 'r') as tac_file:
        input_program = Program(tac_file.read())
        tac_BBlist = input_program.blocks
        tac_edgelist = input_program.edges

        #Add Basic Blocks to the cfg
        add_tac_BasicBlocks(cfg, tac_BBlist)

        #Add Edges to the cfg
        add_tac_edges(cfg, tac_edgelist)
        
    with open(dot_filename, 'w') as dotfile:
        dotfile.write(cfg.to_string())

    # Generate png
    # TODO : support more formats like svg, pdf, jpg
    # NOTE : pydotplus needs the GraphViz binaries to be installed anyway so using them should not be a problem
    # In any case, ensure that the use has GraphViz binaries installed
    _ ,output_format = os.path.splitext(cfg_filename)
    output_format = output_format[1:] #to remove the starting .
    check_call(['dot', '-T{}'.format(output_format), dot_filename, '-o', cfg_filename])

    

