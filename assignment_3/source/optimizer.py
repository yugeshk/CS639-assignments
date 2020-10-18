class OptimizedPrinter():
    def __init__(self):
        self.program_text = '' 
        
    def visit_Module(self, node, program_text):
        self.__init__()
        self.program_text = program_text
        self.indent_level = 0
        self.opt_text = ''
        
        body = node['body']
        self.visit_Statement_Body(body)
    
    def visit_Statement_Body(self, body):
        for stmnt in body:
            self.visit_Generic_Statement(stmnt)
                    
    def visit_Generic_Statement(self, node):
        
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
            raise Exception('Invalid Construct')
                
    def visit_While(self, node):
        self.opt_text += ("\t"*self.indent_level + "while " + node['test']['id'] +" :\n")
        self.indent_level += 1
        #saving the old text to see if any new statements are printed
        old_text = self.opt_text
        self.visit_Statement_Body(node['body'])
        #adding a pass statement in case the body becomes empty
        if(old_text == self.opt_text):
            self.opt_text += ("\t"*self.indent_level + "pass\n")
        self.indent_level -= 1
    
    def visit_Assign(self, node):
        target_phrase = ""
        for target in node['targets']:
            if(not target['dead']):
                target_phrase += (target['id']+' = ')
                
        if(target_phrase != ""):
            self.opt_text += (self.indent_level*"\t"+target_phrase + self.get_node_text(node['value']) +'\n')
    
    def visit_AugAssign(self, node):
        if(not node['dead']):
            self.opt_text += (self.indent_level*"\t"+self.get_node_text(node)+"\n")
    
    def visit_If(self, node):
        self.opt_text += ("\t"*self.indent_level + "if " + node['test']['id'] +" :\n")
        self.indent_level += 1
        #saving the old text to see if any new statements are printed
        old_text = self.opt_text
        self.visit_Statement_Body(node['body'])
        #adding a pass statement in case the body becomes empty
        if(old_text == self.opt_text):
            self.opt_text += ("\t"*self.indent_level + "pass\n")
        self.indent_level -= 1
        
    def visit_If_Else(self, node):
        self.opt_text += ("\t"*self.indent_level + "if " + node['test']['id'] +" :\n")
        self.indent_level += 1
        #saving the old text to see if any new statements are printed
        old_text = self.opt_text
        self.visit_Statement_Body(node['body'])
        #adding a pass statement in case the body becomes empty
        if(old_text == self.opt_text):
            self.opt_text += ("\t"*self.indent_level + "pass\n")
        self.indent_level -= 1
        
        self.opt_text += ("\t"*self.indent_level + "else:\n")
        self.indent_level += 1
        #saving the old text to see if any new statements are printed
        old_text = self.opt_text
        self.visit_Statement_Body(node['orelse'])
        #adding a pass statement in case the body becomes empty
        if(old_text == self.opt_text):
            self.opt_text += ("\t"*self.indent_level + "pass\n")
        self.indent_level -= 1

        
    def visit_Expr(self, node):
        self.opt_text += (self.indent_level*"\t"+self.get_node_text(node)+"\n")
    
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
            