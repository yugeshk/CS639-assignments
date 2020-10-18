import sys
import os

class FaintVariableAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.loc_variables = set() #This is the global set of local variables
        for bb in self.graph.vertices:
            for s in bb.statements:
                self.loc_variables = self.loc_variables.union(s.defined)
                self.loc_variables = self.loc_variables.union(s.used)

        print("These are all the local variables {}".format(self.loc_variables))
        self.Ins = []
        self.Outs = []
        for bb in self.graph.vertices:
            self.Ins.append(self.loc_variables.copy())
            self.Outs.append(self.loc_variables.copy())

        #Now we compute the fix_point
        num_iter = self.run_fixpoint_iteration() #self.Ins and self.Outs are updated
        print("Number of fixpoint iterations required {}".format(num_iter))
        # self.print_all_faints()

    def run_optimizer(self):

        #Loop over all Basic Blocks
        for bb_id in range(0, len(self.graph.vertices)):
            
            #First we compute IN and OUT for each statement
            stmtINs = [set() for s in self.graph.vertices[bb_id].statements]
            stmtOUTs = [set() for s in self.graph.vertices[bb_id].statements]
            num_stmts = len(self.graph.vertices[bb_id].statements)
            currIN = set()
            currOUT = self.Outs[bb_id]
            for stmt_id in range(num_stmts-1, -1, -1):
                stmt = self.graph.vertices[bb_id].statements[stmt_id]
                DepKill = set()
                if(stmt.node == None):
                    #Branch stmt
                    DepKill = set()
                elif(stmt.node['_type'] == 'Assign'):
                    #Assign stmt
                    if stmt.defined.difference(currOUT):
                        DepKill = stmt.used.copy()
                    else:
                        DepKill = set()
                elif(stmt.node['_type'] == 'AugAssign'):
                    #AugAssign stmt
                    if stmt.defined.difference(currOUT):
                        DepKill = stmt.used.copy()
                    else:
                        DepKill = set()
                elif(stmt.node['_type'] == 'Expr'):
                    #Expression
                    DepKill = set()

                currIN = (currOUT.difference(stmt.const_kill.union(DepKill))).union(stmt.const_gen)
                #Update stmtINs and stmtOUTs
                stmtINs[stmt_id] = currIN.copy()
                stmtOUTs[stmt_id] = currOUT.copy()
                
                #Update currOUT for upward propagation
                currOUT = currIN.copy()                          
            
            
            #Loop over all statements of that BasicBlock
            for stmt_id in range(0, num_stmts):
                stmt = self.graph.vertices[bb_id].statements[stmt_id]
                #Assume you have two lists of sets stmtINs and stmtOUTs. Use stmt_id for indexing
                if(stmt.node == None):
                    pass
                elif(stmt.node['_type'] == 'Assign'):
                    if(not stmt.fn_call_present):
                        for target in stmt.node['targets']:
                            if(target['id'] in stmtOUTs[stmt_id]):
                                target['dead'] = True
                            else:
                                target['dead'] = False
                    else:
                        for target in stmt.node['targets']:
                            target['dead'] = False

                elif(stmt.node['_type'] == 'AugAssign'):
                    if(not stmt.fn_call_present):
                        if(stmt.node['target']['id'] in stmtOUTs[stmt_id]):
                            stmt.node['dead'] = True 
                        else:
                            stmt.node['dead'] = False
                    else:
                        stmt.node['dead'] = False
                                            

    def back_prop_basicblock(self, bb_id, newOUT):
        basicblock = self.graph.vertices[bb_id]
        currOUT = newOUT.copy()
        currIN = set()
        for stmt in reversed(basicblock.statements):
            DepKill = set()
            if(stmt.node == None):
                #Branch stmt
                DepKill = set()
            elif(stmt.node['_type'] == 'Assign'):
                #Assign stmt
                if stmt.defined.difference(currOUT):
                    DepKill = stmt.used.copy()
                else:
                    DepKill = set()
            elif(stmt.node['_type'] == 'AugAssign'):
                #AugAssign stmt
                if stmt.defined.difference(currOUT):
                    DepKill = stmt.used.copy()
                else:
                    DepKill = set()
            elif(stmt.node['_type'] == 'Expr'):
                #Expression
                DepKill = set()

            currIN = (currOUT.difference(stmt.const_kill.union(DepKill))).union(stmt.const_gen)
            currOUT = currIN.copy()

        return currOUT
    
    def run_fixpoint_iteration(self):
        num_iterations = 0
        #The FixPoint iteration is monotonic so we expect this loop to always terminate
        while(True):
            num_iterations += 1
            #Initialize newINs and newOUTs
            newINs = []
            newOUTs = []
            for i in range(0, len(self.graph.vertices)):
                newINs.append(self.Ins[i].copy())
                newOUTs.append(self.Outs[i].copy())

            for bb_id in range(0, len(self.graph.vertices)):
                if bb_id == 1:
                    continue #This is the EXIT BasicBlock

                newOUT = self.loc_variables
                newIN = set()
                #First we compute the newOUT for a BasicBlock by taking union over all edges to it
                for e in self.graph.edges:
                    if bb_id == e[0]:
                        newOUT = newOUT.intersection(newINs[e[1]])

                #Next we compute the newIN for a BaiscBlock by propagating the newOUT backwards
                newIN = self.back_prop_basicblock(bb_id, newOUT)

                newINs[bb_id] = newIN.copy()
                newOUTs[bb_id] = newOUT.copy()

            #Now we check if we have reached a FixPoint
            fp = 1
            for i in range(0, len(self.graph.vertices)):
                if i == 1:
                    continue

                if(newINs[i] != self.Ins[i]):
                    fp = 0
                    self.Ins[i] = newINs[i].copy()
                
                if(newOUTs[i] != (self.Outs[i])):
                    fp = 0
                    self.Outs[i] = newOUTs[i].copy()

            if fp == 1:
                break

        return num_iterations

    def print_all_faints(self):

        print(self.graph.edges)

        for bb_id in range(0, len(self.graph.vertices)):
            print("\n")
            print("Faint variables at entry of {} are {}".format(bb_id, self.Ins[bb_id]))
            for s in self.graph.vertices[bb_id].statements:
                print(s.text)
            print("Faint variables at exit of {} are {}".format(bb_id, self.Outs[bb_id]))
        