import json
import sys




class Analyzer():
    def __init__(self):
        self.stats = {"loop_conditions": [], "branch_conditions": [], "assignment_statements":[]}
        self.program_text = ''

    def report_answer(self):
        print("Here is the Answer:\n")
    	
        print('Loop Conditions:')
        print('[line, col]')
        print(('\n').join(self.stats['loop_conditions']))
        print()
        
        print('Branch Conditions:')
        print('[line, col]')
        print(('\n').join(self.stats['branch_conditions']))
        print()
        
        print('AssignmentStatements:')
        print('[line, col]')
        print(('\n').join(self.stats['assignment_statements']))
        print()

    def analyze(self, program_node, program_text):
        self.__init__()
        self.program_text = program_text
        self.generic_visit(program_node)
        
        
    def generic_visit(self, node):
        self.take_action(node)
        if(type(node) == dict):
            for key, value in node.items() :
                if(type(value) == list):
                    for child in value:
                        self.generic_visit(child)
                elif(type(value) == dict):
                    self.generic_visit(value)

    def take_action(self, node):
        if(type(node) == dict and "_type" in node.keys()):
            node_type = node['_type']
            if(node_type == 'For'):
                self.visit_For(node)
            elif(node_type == 'AsyncFor'):
                self.visit_AsyncFor(node)
            elif(node_type == 'While'):
                self.visit_While(node)
            elif(node_type == 'Assign'):
                self.visit_Assign(node)
            elif(node_type == 'AugAssign'):
                self.visit_AugAssign(node)
            elif(node_type == 'AnnAssign'):
                self.visit_AnnAssign(node)
            elif(node_type == 'If'):
                self.visit_If(node)
            elif(node_type == 'IfExp'):
                self.visit_IfExp(node)
            else:
                pass
    
    def visit_For(self, node):
        target = node['target']
        iter_ = node['iter']
        target_text = self.get_node_text(target)
        iter_text = self.get_node_text(iter_)
        self.stats['loop_conditions'].append(self.format_lineno(target)+target_text + ' in ' + iter_text)
        
    def visit_AsyncFor(self, node):
        target = node['target']
        iter_ = node['iter']
        target_text = self.get_node_text(target)
        iter_text = self.get_node_text(iter_)
        self.stats['loop_conditions'].append(self.format_lineno(target)+target_text + ' in ' + iter_text)
    
    def visit_While(self, node):
        test = node['test']
        test_text = self.format_lineno(test) + self.get_node_text(test)
        self.stats['loop_conditions'].append(test_text)
        
    def visit_Assign(self, node):
        text = self.format_lineno(node)+self.get_node_text(node)
        self.stats['assignment_statements'].append(text)
    
    def visit_AugAssign(self, node):
        text = self.format_lineno(node)+self.get_node_text(node)
        self.stats['assignment_statements'].append(text)
    
    def visit_AnnAssign(self, node):
        text = self.format_lineno(node)+self.get_node_text(node)
        self.stats['assignment_statements'].append(text)
    
    def visit_If(self, node):
        test = node['test']
        test_text = self.format_lineno(test) + self.get_node_text(test)
        self.stats['branch_conditions'].append(test_text)
    
    def visit_IfExp(self, node):
        test = node['test']
        test_text = self.format_lineno(test) + self.get_node_text(test)
        self.stats['branch_conditions'].append(test_text)

    
    def subset_program_text(self, line1, col1, line2, col2):
        lines = self.program_text.splitlines()
        if(line1 == line2):
            return lines[line1-1][col1:col2]
        else:
            text = lines[line1-1][col1:]
            for i in range(line1, line2-1):
                text+='\n'
                text+=lines[i]
            
            text+='\n'
            text += lines[line2-1][:col2]
            return text
        
    def get_node_text(self, node):
        l1 = node['lineno']
        l2 = node['end_lineno']
        c1 = node['col_offset']
        c2 = node['end_col_offset']
        return self.subset_program_text(l1, c1, l2, c2)
    
    def format_lineno(self, node):
        return "[" + str(node['lineno']) + " ,"+ str(node['col_offset']) + "]: "

if __name__ == "__main__":
    source_file_address = sys.argv[1]
    json_dump_address = sys.argv[2]

    json_file = open(json_dump_address)
    program_ast = json.loads(json_file.read())
    source_file = open(source_file_address)
    program_text = source_file.read()

    myAnalyzer = Analyzer()
    myAnalyzer.analyze(program_ast, program_text)
    myAnalyzer.report_answer()