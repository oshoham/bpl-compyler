from bpl.code_generator.code_generator import generate_code
from bpl.scanner.scanner import ScannerException
from bpl.parser.parser import ParserException, Parser
from bpl.type_checker.type_checker import TypeCheckerException, type_check
import sys, os

if __name__ == "__main__":
    if len(sys.argv) == 3:
        file_name = sys.argv[1]
        output_file_name = sys.argv[2]
    else:
        print "Error: Not enough arguments supplied to bpl main module."
        sys.exit(1)
    if not file_name.endswith('.bpl'):
        print "Error: File name does not have a .bpl extension!"
        sys.exit(1)
    try:
        input_file = open(file_name)
    except IOError:
        print "Error: File not found!"
        sys.exit(1)
    try: 
        parser = Parser(input_file)
        parse_tree = parser.parse()
    except (ScannerException, ParserException) as e:
        print e.message
        sys.exit(1)
    try:
        type_check(parse_tree)
    except TypeCheckerException as t:
        print t.message
        sys.exit(1)
    #output_file_name = os.path.basename(file_name).rstrip('.bpl') + '.s'
    output_file = open(output_file_name, 'w')
    generate_code(parse_tree, output_file)
    input_file.close()
    output_file.close()
