from bpl.type_checker.type_checker import *
from bpl.scanner.scanner import ScannerException
from bpl.parser.parser import ParserException, Parser
import sys

if __name__ == "__main__":
    file_name = "bpl/test/test3.bpl"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    try:
        input_file = open(file_name)
    except IOError:
        print("Error: File not found!")
        sys.exit()
    try: 
        parser = Parser(input_file)
        parse_tree = parser.parse()
    except (ScannerException, ParserException) as e:
        print e.message
        sys.exit()
    try:
        type_check(parse_tree, True)
    except TypeCheckerException as t:
        print t.message
        sys.exit()
    print parse_tree
    input_file.close()
