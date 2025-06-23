# Import(s)
import os
import time

# Function to get datatype
def get_types(file):
    # List of characters valid in char and empty list for types
    valid_char_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    types = []

    # Open file, get rid of first line, and get number of columns
    with open(file, "r") as f:
        attributes = f.readline().strip("\n").split(",")
        columns = len(attributes)

        # Create list for all cells and types
        cells = []

        # Iterate through each line
        for line in f:
            # Split line into sections
            line = line.strip("\n").split(",")

            # Append each section to cells
            for instance in line:
                cells.append(instance)

    # Calculate number of rows
    rows = len(cells) // columns

    # Iterate once per column and once per row while setting col_type to char by default
    for i in range(columns):
        col_type = "NULL"
        for j in range(rows):

            # Create lowercase variable of cell
            cell = cells[i + j*columns].lower()

            # If you can convert the type to INT or FLOAT (DEC), it is not VARCHAR or CHAR
            try:
                cell = float(cell)
                if col_type != "INT" and col_type != "DEC" and col_type != "NULL":
                    col_type = "VARCHAR"
                    break
                elif cell // 1 == cell:
                    col_type = "INT"
                else:
                    col_type = "DEC"
            except ValueError:
                # Iterate through each character and check if it is CHAR or VARCHAR
                for char in cell:
                    if char not in valid_char_letters:
                        col_type = "VARCHAR"
                        break
                    else:
                        col_type = "CHAR"

                # Break if col_type if VARCHAR
                if col_type == "VARCHAR":
                    break

        # Append column type
        types.append(col_type)

    # Return list of types
    return types


# Function to get restriction
def get_restrictions(file, types):
    # Set restrictions to be initially blank
    restrictions = []

    # Open file
    with open(file, "r") as f:
        # Get list of attributes and number of columns
        attributes = f.readline().strip("\n").split(",")
        columns = len(attributes)

        # Iterate through each cell and get list of cells
        cells = []
        for row in f:
            for cell in row.strip("\n").split(","):
                cells.append(cell)

        # Calculate number of rows
        rows = len(cells) // columns

        # Iterate through each cell in each column and append to column
        for i in range(columns):
            col = []
            for j in range(rows):
                col.append(cells[i + j*columns])

            # Get restrictions by calling appropriate function
            if types[i] == "CHAR" or types[i] == "VARCHAR":
                restrictions.append(f"({char_restr(col)})")
            elif types[i] == "DEC":
                restrictions.append(f"{dec_restr(col)}")
            else:
                restrictions.append("")

        # Return list of restrictions
        return restrictions


# Function for char & varchar restrictions
def char_restr(col):
    # Initially set max_len to zero
    max_len = 0

    # Iterate through each instance and find the max_len
    for inst in col:
        if len(inst) > max_len:
            max_len = len(inst)

    # Return the length of the longest instance
    return max_len


# Function for dec restrictions
def dec_restr(col):
    # Initially set max precision and max scale to zero
    max_prec = 0
    max_scale = 0

    # Iterate through each instance in column
    for item in col:
        # Split between decimal point
        number = item.split(".")

        # Set current precision and scale
        curr_prec = len(number[0]) + len(number[1])
        curr_scale = len(number[1])

        # Reset max precision/scale if needed
        if curr_prec > max_prec:
            max_prec = curr_prec
        if curr_scale > max_scale:
            max_scale = curr_scale

    # Return tuple of max precision and scale
    return max_prec, max_scale


# Function to create DROP statement code
def drop(out_path, files):
    # Create empty code list
    code_list = []

    # Iterate backwards through all files
    for file in files[::-1]:
        code_list.append(f"DROP {file.split(".")[0]};\n")

    with open(out_path, "a") as f:
        f.write("/* DROP Statements */\n")
        f.write(f"{''.join(code_list)}\n")


# Function to create INSERT INTO statement code
def inserts(file, out_path, attributes, types, name):
    # Set code_line to be initially blank
    code_line = []
    # Open file
    with open(file, "r") as f:
        # Skip first line
        f.readline()

        # Iterate for each line (except the first one) in file
        for line in f:
            line = line.strip("\n").split(",")

            # Add INSERT INTOs in code_line
            code_line.append("INSERT ")
            code_line.append("INTO ")
            code_line.append(f'"{name.split(".")[0]}"("{'", "'.join(attributes)}")')

            # Add quotations to CHAR and VARCHAR types and set null
            for i in range(len(line)):
                if (types[i] == "CHAR" or types[i] == "VARCHAR") and line[i] != "NULL":
                    line[i] = f"'{line[i].strip(",").replace("'", "''")}'"

                if line[i] == "":
                    line[i] = "NULL"

            # Add Values to code
            code_line.append(f"\nVALUES({", ".join(line)});\n")

        # Write code_line to code file
        with open(out_path, "a") as f:
            f.write(f"/* Insert Statements for {name.split(".")[0]} */ \n")
            f.write(f'{"".join(code_line)}\n')


# File to generate CREATE TABLE statement code
def tables(out_path, attributes, used_attrs, types, restrictions, name):
    # Set code line
    code_line = ["CREATE", "TABLE", f'"{name.split(".")[0]}"(', "\n"]

    # Iterate through each column
    for i in range(len(types)):
        # Add attribute, type, restriction, and new line to code line
        code_line.append(f'\t"{attributes[i]}" {types[i]}{restrictions[i]},\n')

    # Add remove extra from last type and add PRIMARY KEY
    code_line.append(f'\tPRIMARY KEY ("{attributes[0]}"),\n') # Add primary key
    used_attrs.append([attributes[0], name.split(".")[0]]) # Add primary key to used attributes

    # Check if each type is used or new
    for attribute in attributes:
        # Skip primary key
        if attribute == attributes[0]:
            pass

        # Else iterate through each used attribute
        else:
            for used_attr in used_attrs[:]:
                # If already used, write proper reference
                if attribute == used_attr[0]:
                    code_line.append(f'\tFOREIGN KEY ("{attribute}") REFERENCES "{used_attr[1]}"("{attribute}"),\n')


    # Add proper ending
    code_line[-1] = code_line[-1][:-2] + code_line[-1][-1] # Removes last comma
    code_line.append(");\n\n") # Adds ending

    # Open output file and add to it
    with open(out_path, "a") as f:
        f.write(f"/* Tables for {name.split(".")[0]} */\n") # Comment for tables
        f.write(" ".join(code_line)) # Tables

    # Return used types
    return used_attrs


# Function to create SELECT statement code
def select_state(out_path, files):
    # Create empty code list
    code_list = []

    # Iterate backwards through all files
    for file in files:
        code_list.append(f"SELECT * FROM {file.split(".")[0]};\n")

    with open(out_path, "a") as f:
        f.write("/* SELECT Statements */\n")
        f.write("".join(code_list))


# Main function
def main():
    # Get current working directory and set directory of folder with files
    cwd = os.getcwd()
    directory = "Input"
    out_dir = "Output"
    out_path = os.path.join(cwd, out_dir, "all.sql")

    # Set empty list to store files
    files = []

    # Set used types as empty list
    used_attrs = []

    # Add files to files list
    for file in os.listdir(os.path.join(cwd, directory)):
        files.append(file)

    # Sort files by date modified
    files.sort(key=lambda file: os.stat(os.path.join(directory, file)).st_mtime)

    # Create file
    with open(out_path, "w"):
        pass

    # Start time
    start_time = time.perf_counter()

    # Generate DROP statements
    drop(out_path, files)

    # Iterate through all files stored in directory folder
    for file in files:
        path = os.path.join(cwd, directory, file)

        # Get list of type(s)
        types = get_types(path)

        # Get list of restriction(s)
        restrictions = get_restrictions(path, types)

        # Get attributes
        with open(path, "r") as f:
            attributes = f.readline().strip("\n").split(",")

        # Call tables and inserts functions
        used_attrs = tables(out_path, attributes, used_attrs, types, restrictions, file)
        inserts(path, out_path, attributes, types, file)

    # Generate SELECT statements
    select_state(out_path, files)

    # Print results
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time}")


# Call main function
main()