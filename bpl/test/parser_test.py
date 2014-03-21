from bpl.parser.parser import Parser
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
    parser = Parser(input_file)
    parse_tree = parser.parse()
    print parse_tree
    input_file.close()
