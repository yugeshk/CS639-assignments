class Syntax_Checker():
    def __init__(self):
        pass
        
    def visit_Module(self, node, program_text):
        
        if(type(node)!=dict):
            raise Exception('Input type must be a dict')
        
        #Check Program Type is Module
        try:
            program_type = node['_type']
        except:
            raise Exception('Input AST dictionary must have a key "_type"')
        if(program_type != 'Module'):
            raise Exception('Input Program must be of type Module')
        
        #Check type_ignores are empty, as we are not allowing them in the modified grammar for python --
        try:
            type_ignores = node['type_ignores']
        except:
            raise Exception('Input AST dictionary must have a key "type_ignores"')
        if(len(type_ignores) != 0):
            raise Exception('type_ignores are not allowed. Please remove them')
        
        #Check that the program is non-empty
        try:
            body = node['body']
        except:
            raise Exception('Input AST dictionary must have a key "body"')
        if(len(body) == 0):
            raise Exception('Program is empty')
            
        #Do syntax Checking on each statement in the body
        self.visit_Statement_Body(body)
        
        #If no error raised above, the syntax is correct
        print("Program is syntactically correct")
        
    def visit_Statement_Body(self, body):
        if(type(body) != list):
            raise Exception('Invalid AST, type of body must be a list')
            
        for stmnt in body:
            self.visit_Generic_Statement(stmnt)
        
    def visit_Generic_Statement(self, node):
        
        #Check type of node is dict
        if(type(node)!=dict):
            raise Exception('Statement node must be of type dict')
        
        #Check the "_type" key is present
        try:
            stmnt_type = node['_type']
        except:
            raise Exception('Statement node dictionary must have a key "_type"')
            
        #Checking if the statement is in one of the allowed constructs according to the grammar
        if(stmnt_type == 'While'):
            self.visit_While(node)
        elif(stmnt_type == 'Assign'):
            self.visit_Assign(node)
        elif(stmnt_type == 'AugAssign'):
            self.visit_AugAssign(node)
        elif(stmnt_type == 'If'):
            if(len(node['orelse']) == 0):
                self.visit_If(node)
            else:
                self.visit_If_Else(node)
        elif(stmnt_type == 'Expr'):
            self.visit_Expr(node)
        else:
            try:
                lineno = node['lineno']
            except:
                raise Exception('Statement node dictionary must have a key "lineno"')
                
            raise Exception('Invalid statement of type: '+stmnt_type+' on line: '+str(lineno))
            
    def visit_While(self, node):
        #Syntax Check to make sure that condition is a Variable, according to Python -- grammar
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for While statement on line: '+ str(node['lineno'])+ " is not A variable")
            
        #Syntax Check to make sure that orelse if empty according to Python -- grammar
        orelse = node['orelse']
        if(len(orelse) != 0):
            raise Exception('Orelse for While statement on line: '+ str(node['lineno'])+ " is not allowed")
            
        #Check the body of the while loop
        body = node['body']
        self.visit_Statement_Body(body)
    
    def visit_Assign(self, node):
        #Syntax Check to make sure that the LHS(target) of assignment, is variable only, 
        #and not lists, tuples, starred
        targets = node['targets']
        for target in targets:
            if(target['_type'] != 'Name'):
                raise Exception("The target for assignment on line: "+str(node['lineno'])+" is not a variable")
        self.check_Expr_Syntax(node['value'])
        
    def visit_AugAssign(self, node):
        target = node['target']
        if(target['_type'] != 'Name'):
            raise Exception("The target for assignment on line: "+str(node['lineno'])+" is not a variable")
        self.check_Expr_Syntax(node['value'])
        
            
    def visit_If(self, node):
        #Syntax Check to make sure that condition is a Variable
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for if statement on line: '+ str(node['lineno'])+ " is not a variable")
        
        #Check the body of the if statement
        body = node['body']
        self.visit_Statement_Body(body)
        
    
    def visit_If_Else(self, node):
        #Syntax Check to make sure that condition is a Variable
        test = node['test']
        if(test['_type']!='Name'):
            raise Exception('Test for if statement on line: '+ str(node['lineno'])+ " is not A variable")
            
        #Check the body of the if statement
        body = node['body']
        self.visit_Statement_Body(body)
        
        #Check the else body of the if statement
        orelse = node['orelse']
        self.visit_Statement_Body(orelse)
        #Now Syntax Check has been done
        
    def visit_Expr(self, node):
        if(node['value']['_type']!='Call'):
            raise Exception('''Only functions calls and assignment statements are allowed, but an invalid 
                            expression statement found on line: ''' + str(node['lineno']))
        self.check_Expr_Syntax(node['value'])
    
    def check_Expr_Syntax(self, node):
        if(node['_type'] == 'BoolOp'):
            self.visit_BoolOp(node)
        elif(node['_type'] == 'BinOp'):
            self.visit_BinOp(node)
        elif(node['_type'] == 'UnaryOp'):
            self.visit_UnaryOp(node)
        elif(node['_type'] == 'Compare'):
            self.visit_Compare(node)
        elif(node['_type'] == 'Call'):
            self.visit_Call(node)
        elif(node['_type'] == 'Constant'):
            pass # It is fine
        elif(node['_type'] == 'Name'):
            pass # It is fine
        else:
            raise Exception('Invalid Expression type on line: '+str(node['lineno'])+" col: "+str(node['col_offset']))
            
    def visit_BoolOp(self, node):
        for value in node['values']:
            self.check_Expr_Syntax(value)
            
    def visit_BinOp(self, node):
        self.check_Expr_Syntax(node['right'])
        self.check_Expr_Syntax(node['left'])
    
    def visit_UnaryOp(self, node):
        self.check_Expr_Syntax(node['operand'])
    
    def visit_Call(self, node):
        for arg in node['args']:
            self.check_Expr_Syntax(arg)
            
        for keyword in node['keywords']:
            self.check_Expr_Syntax(keyword['value'])
            
    def visit_Compare(self, node):
        self.check_Expr_Syntax(node['left'])
        for cmp in node['comparators']:
            self.check_Expr_Syntax(cmp)
            
