from translator import Translator
from translator import remove_infeasible_labels
import sys
import json
from program import Program

 
if __name__ == "__main__":
    source_file_address = sys.argv[1]
    json_dump_address = sys.argv[2]

    json_file = open(json_dump_address)
    program_ast = json.loads(json_file.read())
    source_file = open(source_file_address)
    program_text = source_file.read()

    myTranslator = Translator()
    threeAC = myTranslator.visit_Module(program_ast, program_text)
    threeAC = remove_infeasible_labels(threeAC, myTranslator.jump_targets)
    
    myProgram = Program(threeAC)
