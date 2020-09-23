from ast2json import *
import json
import ast

class Translator():
    def __init__(self):
        self.label = 1
        self.program_text = '' 
        self.jump_targets = set()
        
    def new_label(self):
        self.label += 1
        return self.label-1
    
    def label_str(self, label_num):
        return "L"+str(label_num)+": " 
    
    def gen_goto(self, label_num):
        self.jump_targets.add(label_num)
        return "goto L"+ str(label_num)+"\n"
        
    def visit_Module(self, node, program_text):
        self.__init__()
        self.program_text = program_text
        
        if(type(node)!=dict or node['_type']!='Module'):
            raise Exception('Input type must be a dict and root node should be of type Modules')
        else:
            body = node['body']
            if(len(body) == 0):
                raise Exception('Empty Program')
            else:
                for stmnt in body:
                    stmnt['next'] = self.new_label()
                for stmnt in body:
                    self.visit_Generic_Statement(stmnt)
                    
                node['code'] = ''
                for stmnt in body:
                    node['code'] += stmnt['code']
                    node['code'] += self.label_str(stmnt['next'])
                return node['code']
    
    def visit_Stament_Body(self, body, next_label):
        if(len(body) == 0):
            raise Exception('body is Empty')
        else:
            for stmnt_num in range(len(body)-1):
                body[stmnt_num]['next'] = self.new_label()
            #the next for the last statement must be next_label
            body[-1]['next'] = next_label
            for stmnt in body:
                    self.visit_Generic_Statement(stmnt)
                    
            code = ''
            for stmnt_num in range(len(body)-1):
                code += body[stmnt_num]['code']
                code += self.label_str(body[stmnt_num]['next'])
            #Note that the label for the last statement is not added
            code+=body[-1]['code']
            return code
                    
    def visit_Generic_Statement(self, node):
        if(type(node) == dict and "_type" in node.keys()):
            node_type = node['_type']
            if(node_type == 'While'):
                self.visit_While(node)
            elif(node_type == 'Assign'):
                self.visit_Assign(node)
            elif(node_type == 'AugAssign'):
                self.visit_AugAssign(node)
            elif(node_type == 'AnnAssign'):
                self.visit_AnnAssign(node)
            elif(node_type == 'If'):
                if(len(node['orelse']) == 0):
                    self.visit_If(node)
                else:
                    self.visit_If_Else(node)
            elif(node_type == 'Expr'):
                self.visit_Expr(node)
            else:
                raise Exception('Invalid Construct on Line')
        else:
            raise Exception("Node must be of type dict")
                
    def visit_While(self, node):
        #Syntax Check to make sure that condition is a Variable
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for if statement on line: '+ str(node['lineno'])+ " is not A variable")
        #Now Syntax Check has been done
        
        #We generate code for test
        begin = self.new_label()
        test['true'] = self.new_label()
        test['false'] = node['next']
        self.visit_Test(test)
        
        #Now generate code for loop body
        body = node['body']
        body_code = self.visit_Stament_Body(body, begin)
        
        #Now we genrate code for the Whole of While Loop
        node['code'] = 'noOp\n' #I've added NoOp to make sure every stattement has only one label
        node['code'] += self.label_str(begin)
        node['code'] += test['code']
        node['code'] += self.label_str(test['true'])
        node['code'] += body_code
        node['code'] += self.gen_goto(begin)
        
    def visit_Assign(self, node):
        node['code'] = self.get_node_text(node) + '\n'
    
    def visit_AugAssign(self, node):
        node['code'] = self.get_node_text(node) + '\n'
    
    def visit_AnnAssign(self, node):
        node['code'] = self.get_node_text(node) + '\n'
        
    def visit_Test(self, node):
        node['code'] = "if "+ node['id']+ " then " + self.gen_goto(node['true'])+ self.gen_goto(node['false'])
    
    def visit_If(self, node):
        #Syntax Check to make sure that condition is a Variable
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for if statement on line: '+ str(node['lineno'])+ " is not A variable")
        #Now Syntax Check has been done
        
        #We generate code for test
        test['true'] = self.new_label()
        test['false'] = node['next']
        self.visit_Test(test)
        
        #Now we generate code for body
        body = node['body']
        body_code = self.visit_Stament_Body(body, node['next'])#We pass the next attribute as written in the grammar
        
        #Now we genrate code for the Whole of If
        node['code'] = ''
        node['code'] += test['code']
        node['code'] += self.label_str(test['true'])
        node['code'] += body_code
    
    def visit_If_Else(self, node):
        #Syntax Check to make sure that condition is a Variable
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for if statement on line: '+ str(node['lineno'])+ " is not A variable")
        #Now Syntax Check has been done
        
        #We generate code for test
        test['true'] = self.new_label()
        test['false'] = self.new_label()
        self.visit_Test(test)
        
        #Now we generate code for if body
        if_body = node['body']
        if_body_code = self.visit_Stament_Body(if_body, node['next'])#We pass the next attribute as written in the grammar
        
        #Now generate code for else body
        else_body = node['orelse']
        else_body_code = self.visit_Stament_Body(else_body, node['next'])
        
        #Now we genrate code for the Whole of If
        node['code'] = ''
        node['code'] += test['code']
        node['code'] += self.label_str(test['true'])
        node['code'] += if_body_code
        node['code'] += self.gen_goto(node['next'])
        node['code'] += self.label_str(test['false'])
        node['code'] += else_body_code
        
    def visit_Expr(self, node):
        if(node['value']['_type']!='Call'):
            raise Exception('Only functions calls and assignment statements are allowed')
        else:
            node['code'] = self.get_node_text(node) + '\n'
    
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
        return "At line " + str(node['lineno']) + " :"
            
    
