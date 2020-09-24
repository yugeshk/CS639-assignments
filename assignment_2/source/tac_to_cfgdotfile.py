"""
Converts a Three-Address-Code file to CFG and outputs as .dot and .png
Usage : python tac_to_cfgdotfile.py <filename>.tac <filename>.dot <filename>.png
"""

import sys
import os
import pydotplus
from subprocess import check_call

#Global variables
tac_filename = sys.argv[1]
dot_filename = sys.argv[2]
png_filename = sys.argv[3]

class Statement():
    def __init__(self, text, line_index):
        self.text = text
        #Line_index starts at 0
        self.line_index = line_index
        
    def is_leader(self, program):
        if(self.line_index == 0):
            #The first stmnt
            return True
        elif(program.statements[self.line_index - 1].is_jump()):
            #Is previous line jump
            return True
        elif(self.is_target()):
            return True
        else:
            return False
            
    def is_jump(self):
        if(self.text.find("goto L") >= 0):
            return True
        else:
            return False
        
    def is_unconditional_jump(self):
        if(self.is_jump() and not(self.text.find('then goto L')>=0)):
            return True
        else:
            return False
        
    def get_statement_jump_target(self):
        if(self.is_jump()):
            return int(self.text.split('goto L')[1])
        else:
            raise Exception('Cant get target if statement is not jump')
            
    
    def get_statement_label(self):
        if(self.is_target()):
            return int(self.text.split(':')[0].split('L')[1])
        else:
            raise Exception('Cant get label if statement is not target')
    
    def is_target(self):
        if(self.text.find(':') >= 0):
            return True
        else:
            return False
        
    
class BasicBlock():
    def __init__(self, statements):
        self.statements = statements
        
    def get_text(self):
        text = ''
        for stmnt in self.statements:
            text += (stmnt.text + '\n')
        return text

class Program():
    def __init__(self, program_text):
        self.program_text = program_text
        self.statements = []
        program_lines = program_text.split('\n')
        for i in range(len(program_lines)):
            self.statements.append(Statement(program_lines[i], i))
        self.blocks = self.make_blocks()
        self.edges = self.make_edges()
        
    def make_blocks(self):
        blocks = []
        if(len(self.statements) == 0):
            return []
        else:
            for i in range(len(self.statements)):
                if(i == 0):
                    curr_block = []
                    curr_block.append(self.statements[i])
                elif(self.statements[i].is_leader(self)):
                    blocks.append(BasicBlock(curr_block))
                    curr_block = []
                    curr_block.append(self.statements[i])
                else:
                    curr_block.append(self.statements[i])
            blocks.append(BasicBlock(curr_block))
            return blocks
        
    def is_edge(self,i, j):
        #if i end in jump going to j
        if(self.blocks[i].statements[-1].is_jump() and self.blocks[j].statements[0].is_target()):
            jump_target = self.blocks[i].statements[-1].get_statement_jump_target()
            jump_label = self.blocks[j].statements[0].get_statement_label()
            if(jump_target == jump_label):
                return True
        
        #if i does not end in jump, and j follows i, i.e, j == i+1
        if(not(self.blocks[i].statements[-1].is_unconditional_jump()) and (j == i+1)):
            return True
        
        return False
            
        
    def make_edges(self):
        edges = []
        for i in range(len(self.blocks)):
            for j in range(len(self.blocks)):
                if(self.is_edge(i, j)):
                    edges.append((i, j))
        return edges

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
    cfg_attrs = {'label': 'CFG for {}'.format(tac_filename)}
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
    check_call(['dot', '-Tpng', dot_filename, '-o', png_filename])

    

