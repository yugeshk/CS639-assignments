#!/usr/bin/env python
#vim: set ts=2 sts=2 sw=2 et si tw=80:
import re
import sys
import subprocess
import string
import numpy as np


#Build a CFG for a function based on objdump -d output
#usage: objdump_to_cfg.py "objdump -d output" function_name

jumps = [ "ja","jnbe","jae","jnb","jnc","jb","jnae","jc","jbe","jna","jcxz","jecxz","je","jz","jg","jge","jnle","jl","jnge", "jle","jnl","jne","jnz","jng","jno","jnp","jpo","jns","jo","jp","jpe","js" ]
jumps_uncond = ["jmp","jmpq"]
calls = ["call","callq"]
rets = ["ret","retq","repz","repz ret","repz retq"]
dump_file = sys.argv[1]
root_name = sys.argv[2] #The function that will be the root of our CFG

#Regular Expression to map function names in the disassembled code
symbol_re = re.compile("^([a-fA-F0-9]+) <([\.\w]+)>:\s*$")

#print "#address;[target1, target2, ...]" #our output format
#print "#0 == root, -1 == indirect" #right now we only use indirects as sources

#CFG: key is source address, values are all targets
CFG={}

root=-1 #The root of our CFG

#Store the objdump in memory, list of tuples (address, asm)
#Went with this over a dict since we should be iterating more than searching
#so having it sorted by address just makes sense
objdump=[] #List of assembly instructions in the function
indirects=[] #List of indirect calls or jumps
calls_ctr=[]
blockqueue=[] #Stack of program counters to trace
paths_visited=[]
starting_points=[] #List of starting points of a BB
basic_blocks=[] #List of BBs
basic_block_ctr = 0
ending_points=[] #List of ending points of a BB
ending_points_targets=[] #List of targets of an endpoint, to construct CFG
#Offset to add to all addresses. this is 32bit ELF w/o ASLR
#offset=0x80000000
#offset=0x00000000

def main():
    global root
    global blockqueue
    with open(dump_file) as f:
        begin_dump=0
        for line in f:
            #First find out function of interest
            m=symbol_re.match(line)
            if(m):
                print(m)
                if(begin_dump == 1):
                    begin_dump =2
                if(m.group(2) == root_name):
                    # import ipdb; ipdb.set_trace()
                    print(m.group(1), m.group(2))
                    root=int(m.group(1),16)
                    begin_dump=1

            #Example tab-delimited output from objdump:
            #ADDRESS    INSTRUCTION           ASCII
            #c1000000:  8b 0d 80 16 5d 01     mov    0x15d1680,%ecx
            fields = line.rstrip().split('\t')

            #Instructions have 3  fields, but their actual function names have only 1
            if(len(fields)<3):
                continue

            #objdump -d is a linear disassembler, so we every we get will already be
            #sorted by address.

            #Our in-memory representation of objdump output is an list of tuples of
            #the form (address, instruction)
            #Note that we store the address in int form for searching
            if(begin_dump == 1):
                objdump.append((int(fields[0].replace(":",""),16), fields[2]))

        if(root==-1):
            print("Could not find root function for CFG: {}".format(root_name))

        blockqueue.append(root) #queue is technically a stack, but whatever
        while(len(blockqueue)>0):
            block=blockqueue.pop()
            iterate_bb(block)

        #print_starting_points()
        print_basic_blocks()
        #print_ending_points()
        #print_ending_points_targets()
        generate_CFG()
        print_CFG_stats()
        print_textfile()
        print("Calls: %d"%len(calls_ctr))
        print("%s"%array_to_hex(calls_ctr))
        print("Indirect calls/jumps: %d"%len(indirects))
        print("%s"%array_to_hex(indirects))

####END MAIN BEGIN FUNCTION DEFS#####
def array_to_hex(array):
    return "".join('0x%x' % i for i in array)

def print_CFG_stats():
    print("CFG has %d nodes" %(basic_block_ctr))
    for x in range(0,basic_block_ctr):
        for y in range(0,basic_block_ctr):
            if(CFG[x,y] == 1):
                print("Node %d can jump to Node %d" %(x,y))

def escape_string(inp_string):
    """Helper function to escape characters for the DOT language"""

    return inp_string.translate(str.maketrans({'"': r'\"', "&": r"\&", "<": r"\<", ">": r"\>"}))

def print_textfile():
    textfile=root_name+".graph"
    with open( textfile, "w") as text_file:
        text_file.write("digraph G { \n")
        for x in range(0,basic_block_ctr):
            # Initialize node in the dot language format
            # Add tooltip, not sure why, also add shape and declare label
            text_file.write("Node%d [ tooltip = \"%s to %s\"; shape=record; label=\"{%s:\l "%(x,hex(basic_blocks[x][1]),hex(basic_blocks[x][2]),hex(basic_blocks[x][1])))
            # import ipdb; ipdb.set_trace();
            # Add all the instructions as a label
            for temp in range(0, len(objdump)):
                if objdump[temp][0] == basic_blocks[x][1]:
                    break
            curr_instr_index = temp
            while objdump[curr_instr_index][0] <= basic_blocks[x][2]:
                text_file.write("{}\l".format(escape_string(objdump[curr_instr_index][1])))
                curr_instr_index += 1
                if(curr_instr_index > len(objdump)):
                    break
            #close the label
            text_file.write("}\"];\n")
            for y in range(0,basic_block_ctr):
                if(CFG[x,y] == 1):
                    text_file.write("Node%d -> Node%d\n"%(x,y))

        text_file.write("}\n")

def print_starting_points():
    a = 0
    print("Starting points")
    for x in starting_points:
        print(hex(x))
        a = a+1

    print("Number of basic blocks = %d"%(a))

def print_basic_blocks():
    print("Basic Blocks")
    bb_file=root_name+"_bb.txt"
    with open(bb_file,"w") as bb_out:
        for x in basic_blocks:
            bb_out.write("%s %s %s %s\n" %(x[0],hex(x[1]),hex(x[2]),x[2]-x[1]))

def print_ending_points():
    print("Ending points")
    for x in ending_points:
        print(hex(x))

def print_ending_points_targets():
    print("Ending point targets")
    for x in ending_points_targets:
        print(hex(x[0]),hex(x[1]))

def initialise_CFG():
    for x in range(0,basic_block_ctr):
        for y in range(0,basic_block_ctr):
            CFG[x,y] = 0

def get_objdump_index(address):
    #Takes in an address and finds the index in the objdump array. The objdump array is sorted
    #Binary search in our array to find our target
    item = 0
    first = 0
    last = len(objdump)-1
    while first<=last:
        mid = (int)((first+last)/2)
        item = objdump[mid][0]
        if(item==address):
            return mid
        else:
            if(address < item):
                last = mid-1
            else:
                first = mid+1

    print("Couldn't find address:%s"%(address))

def print_instr(instr):
    #Useful for debugging
    print("0x%x: %s"%(objdump[instr][0],objdump[instr][1]))

def count_indirect(source_addr):
    global indirects
    indirects.append(source_addr)

def count_calls(source_addr):
    global calls_ctr
    calls_ctr.append(source_addr)

def iterate_bb(block_addr):
    global blockqueue
    global CFG
    global paths_visited
    global starting_points
    global basic_blocks
    global basic_block_ctr
    global ending_points
    global ending_points_targets
    if( block_addr==-1):
        #Stop conditions: we return to root or an indirect (somehow)
        return

    if(block_addr in starting_points):
        #Loop detection
        return

    starting_points.append(block_addr)

    #Now, step through until we hit a jump, call, or ret
    for i in range(get_objdump_index(block_addr),len(objdump)):
        target_hex=0
        split = objdump[i][1].split()
        instr=split[0]
        #Got the opcode out
        #print(instr)
        if(len(split)>=2):
            target = split[1]
            try:
                target_hex = int(target,16)
            except:
                #already an int or an indirect (which won't be used)
                target_hex = target


        #Look for conditional jumps
        if(instr in jumps):
        #print(hex(block_addr),target_hex)
            if '*' in target:
            #Indirect jump, beyond scope of code
                count_indirect(objdump[i][0])
                print("Indirect jump")
                print(objdump[i][1])
	            #Add Basic Block
	            #basic_blocks.append((basic_block_ctr,block_addr,objdump[i][0]))
	            #basic_block_ctr = basic_block_ctr + 1
	            #ending_points.append(objdump[i][0])
                return
            else:
                #Handle jump not taken
                blockqueue.append(objdump[i+1][0])
                #Handle jump taken
                blockqueue.append(target_hex)
	            #Add Basic Block
                basic_blocks.append((basic_block_ctr,block_addr,objdump[i][0]))
                basic_block_ctr = basic_block_ctr + 1
                ending_points.append(objdump[i][0])
                ending_points_targets.append((objdump[i][0],objdump[i+1][0]))
                ending_points_targets.append((objdump[i][0],target_hex))
                return

        #Look for unconditional jumps
        if(instr in jumps_uncond):
            #print(hex(block_addr),target_hex)
            blockqueue.append( target_hex )
            #Add Basic Block
            basic_blocks.append((basic_block_ctr,block_addr,objdump[i][0]))
            basic_block_ctr = basic_block_ctr + 1
            ending_points.append(objdump[i][0])
            ending_points_targets.append((objdump[i][0],target_hex))
            return

        if(instr in rets):
            #Add Basic Block
            #print(hex(block_addr),"return")
            basic_blocks.append((basic_block_ctr,block_addr,objdump[i][0]))
            basic_block_ctr = basic_block_ctr + 1
            ending_points.append(objdump[i][0])
            return

        if(instr in calls):
            count_calls(objdump[i][0])
            if '*' in target:
                #Indirect call, beyond scope of code
                print("Indirect call")
                print(objdump[i][1])
                count_indirect(objdump[i][0])
            else:
                print("Call")
                print(objdump[i][1])

        if(i==len(objdump)):
            basic_blocks.append((basic_block_ctr,block_addr,objdump[i-2][0]))
            basic_block_ctr = basic_block_ctr + 1
            ending_points.append(objdump[i-2][0])

def generate_CFG():
    global CFG
    global starting_points
    global ending_points
    global ending_points
    i = -1
    initialise_CFG()
    # import ipdb; ipdb.set_trace();
    for x in ending_points:
        i=i+1

        targets=[]
        for y in ending_points_targets:
            if(y[0]==x):
                targets.append(y[1])

        for z in targets:
            CFG[i,(starting_points.index(z))] = 1

main()
