from bpl.type_checker.type_checker import TypeChecker
import sys

if __name__ == "__main__":
    file_name = "bpl/test/test3.bpl"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    try:
        input_file = open(file_name)
    except IOError:
        print("Error: File not found!")
        exit()
    type_checker = TypeChecker(input_file)
    type_checker.add_decs_to_symbol_table()
    print type_checker.symbol_table
    input_file.close()
