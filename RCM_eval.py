import rcmpy


def main():
    # Read in the file
    with open("test_case_7.txt", 'r') as file:
        code = file.read()

   
    print("\nkeep newlines+spaces:", rcmpy.keep_newlines_spaces(code))
    print("\nkeep newlines:", rcmpy.keep_newlines(code))
    print("\nkeep nothing: (THIS CHANGES LINECOUNT)", rcmpy.keep_nothing(code))


main()