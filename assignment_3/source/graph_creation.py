class VariableFinder():
    def findVariables(self, node):
        if(node['_type'] == 'BoolOp'):
            return self.visit_BoolOp(node)
        elif(node['_type'] == 'BinOp'):
            return self.visit_BinOp(node)
        elif(node['_type'] == 'UnaryOp'):
            return self.visit_UnaryOp(node)
        elif(node['_type'] == 'Compare'):
            return self.visit_Compare(node)
        elif(node['_type'] == 'Call'):
            return self.visit_Call(node)
        elif(node['_type'] == 'Constant'):
            return set()
        elif(node['_type'] == 'Name'):
            return set([node['id']])
            
    def visit_BoolOp(self, node):
        ans = set()
        for value in node['values']:
            ans = ans.union(self.findVariables(value))
        return ans
            
    def visit_BinOp(self, node):
        ans = set()
        ans = ans.union(self.findVariables(node['right']))
        ans = ans.union(self.findVariables(node['left']))
        return ans
    
    def visit_UnaryOp(self, node):
        ans = set()
        ans = ans.union(self.findVariables(node['operand']))
        return ans
    
    def visit_Call(self, node):
        ans = set()
        for arg in node['args']:
            ans = ans.union(self.findVariables(arg))
            
        for keyword in node['keywords']:
            ans = ans.union(self.findVariables(keyword['value']))
            
        return ans
            
    def visit_Compare(self, node):
        ans = set()
        ans = ans.union(self.findVariables(node['left']))
        for cmp in node['comparators']:
            ans = ans.union(self.findVariables(cmp))
        
        return ans
    

class Statement():
    def __init__(self, text, node):
        self.text = text
        self.node = node
        self.defined = set()
        self.used = set()
        var_finder = VariableFinder()
        if(node == None):
            self.defined = set()
            self.used = text.split('[')[1].split(']')[0]
        elif(node['_type'] == 'Assign'):
            self.defined = set()
            for target in node['targets']:
                self.defined = self.defined.union([target['id']])
                
            self.used = var_finder.findVariables(node['value'])
            
        elif(node['_type'] == 'AugAssign'):
            self.defined = set()
            self.defined = self.defined.union([node['target']['id']])
            
            self.used = set()
            self.used = self.used.union([node['target']['id']])
            self.used = self.used.union(var_finder.findVariables(node['value']))
        
        elif(node['_type'] == 'Expr'):
            self.defined = set()
            self.used = var_finder.findVariables(node['value'])

class BasicBlock():
    def __init__(self):
        self.statements = []
    
    def add(self, statement):
        self.statements.append(statement)
        
    def get_text(self):
        text = ''
        for stmnt in self.statements:
            text += ((stmnt.text)+'\n')
        return text
    
class Graph():
    def __init__(self):
        self.vertices = []
        self.edges = []
    
    def new_vertex(self):
        block = BasicBlock()
        self.vertices.append(block)
        return len(self.vertices) - 1
    
    def new_edge(self, ind1, ind2):
        assert(type(ind1) == int)
        assert(type(ind2) == int)
        self.edges.append((ind1, ind2))

        

class GraphGenerator():
    def __init__(self):
        self.program_text = '' 
    
    def init_graph(self):
        self.graph = Graph()
        self.curr_block_index = self.graph.new_vertex()#entry
        self.next_block_index = self.graph.new_vertex()#exit
        
    def visit_Module(self, node, program_text):
        self.__init__()
        self.init_graph()
        self.program_text = program_text
        
        if(type(node)!=dict or node['_type']!='Module'):
            raise Exception('Input type must be a dict and root node should be of type Modules')
        else:
            body = node['body']
            if(len(body) == 0):
                raise Exception('Empty Program')
            else:
                self.visit_Statement_Body(body)
    
    def visit_Statement_Body(self, body):
        for stmnt in body:
            self.visit_Generic_Statement(stmnt)
        
        #add edge from curr block to next block
        self.graph.new_edge(self.curr_block_index, self.next_block_index)
                    
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
        test_variable = node['test']['id']
        
        #create 3 new blocks, header, body, fallthrough
        header_block_index = self.graph.new_vertex()
        body_block_index = self.graph.new_vertex()
        fallthrough_block_index = self.graph.new_vertex()
        
        #add the brach statement in the header
        header_block = self.graph.vertices[header_block_index]
        header_block.add(Statement('brach['+test_variable+']', None))
        
        #add edge from curr to header and from header to falltrogh and body
        self.graph.new_edge(self.curr_block_index, header_block_index)
        self.graph.new_edge(header_block_index, body_block_index)
        self.graph.new_edge(header_block_index, fallthrough_block_index)
        
        #save the old next
        old_next_index = self.next_block_index
        
        #make the header as the next and body as curr and call function again
        self.next_block_index = header_block_index
        self.curr_block_index = body_block_index
        self.visit_Statement_Body(node['body'])
        
        #make the old next as next and call it on falltrough
        self.next_block_index = old_next_index
        self.curr_block_index = fallthrough_block_index
        
        
    def visit_Assign(self, node):
        curr_block = self.graph.vertices[self.curr_block_index]
        curr_block.add(Statement(self.get_node_text(node), node))
    
    def visit_AugAssign(self, node):
        curr_block = self.graph.vertices[self.curr_block_index]
        curr_block.add(Statement(self.get_node_text(node), node))
    
    def visit_If(self, node):
        #add the brach condition to the current block
        test_variable = node['test']['id']
        curr_block = self.graph.vertices[self.curr_block_index]
        curr_block.add(Statement('brach['+test_variable+']', None))
        
        #create 2 new blocks
        true_block_index = self.graph.new_vertex()
        fallthrough_block_index = self.graph.new_vertex()
        
        #add edge from curr_block to true_block and from curr_block to fallthrough
        #also note that edge will be added from falltrhough to next later as fallthrough will become curr
        #edge will be added from true to fallthrough when code if generated for body of this if 
        self.graph.new_edge(self.curr_block_index, true_block_index)
        self.graph.new_edge(self.curr_block_index, fallthrough_block_index)
        
        
        #make curr_block = true block and fall through block next block(bot save the old next) and restore it later
        self.curr_block_index = true_block_index
        old_next_index = self.next_block_index
        self.next_block_index = fallthrough_block_index
        
        #now traverse the body of if, note that curr and next have been set correctly above,
        #and an edge will be added from curr to next there
        self.visit_Statement_Body(node['body'])
        
        
        #set curr to fallthrough and restore next
        self.curr_block_index = fallthrough_block_index
        self.next_block_index = old_next_index

    def visit_If_Else(self, node):
        #add the brach condition to the current block
        test_variable = node['test']['id']
        curr_block = self.graph.vertices[self.curr_block_index]
        curr_block.add(Statement('brach['+test_variable+']', None))
        
        #create 3 blocks
        true_block_index = self.graph.new_vertex()
        false_block_index = self.graph.new_vertex()
        intermeddiate_block_index = self.graph.new_vertex()
        
        #add edge from curr_block to true_block and from curr_block to false_block
        #also note that edge will be added from true to int and false to int later in a recursive call
        #edge will be added from int to next later
        self.graph.new_edge(self.curr_block_index, true_block_index)
        self.graph.new_edge(self.curr_block_index, false_block_index)
        
        #make next = int block and save the old block
        old_next_index = self.next_block_index
        self.next_block_index = intermeddiate_block_index
        self.curr_block_index = true_block_index
        #do reursive call
        self.visit_Statement_Body(node['body'])
        
        #change curr to false block and again do recursive call
        self.curr_block_index = false_block_index
        self.visit_Statement_Body(node['orelse'])
        
        #set curr to int and restore next
        self.curr_block_index = intermeddiate_block_index
        self.next_block_index = old_next_index
        
        
    def visit_Expr(self, node):
        curr_block = self.graph.vertices[self.curr_block_index]
        curr_block.add(Statement(self.get_node_text(node), node))
    
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
