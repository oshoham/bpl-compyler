from bpl.parser.parser import Parser
import sys

if __name__ == "__main__":
    file_name = "bpl/test/test.bpl"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    try:
        input_file = open(file_name)
    except IOError:
        print("Error: File not found!")
        exit()
    parser = Parser(input_file)
    # test parser here
    input_file.close()