# Import(s)
import os

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
                if (col_type != "INT" and col_type != "DEC" and col_type != "NULL"):
                    col_type = "VARCHAR"
                    break
                elif (cell // 1 == cell):
                    col_type = "INT"
                else:
                    col_type = "DEC"
            except ValueError:
                # Iterate through each character and check if it is CHAR or VARCHAR
                for char in cell:
                    if (char not in valid_char_letters):
                        col_type = "VARCHAR"
                        break
                    else:
                        col_type = "CHAR"

                # Break if col_type if VARCHAR
                if (col_type == "VARCHAR"):
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
            if (types[i] == "CHAR" or types[i] == "VARCHAR"):
                restrictions.append(f"({char_restr(col)})")
            elif (types[i] == "DEC"):
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
        if (len(inst) > max_len):
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
        if (curr_prec > max_prec):
            max_prec = curr_prec
        if (curr_scale > max_scale):
            max_scale = curr_scale

    # Return tuple of max precision and scale
    return ((max_prec, max_scale))


# Function to create insert statement code
def inserts(file, out_path, attributes, types):
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
            code_line.append("INSERT")
            code_line.append("INTO")
            code_line.append(f'"{out_path.split("\\")[-1].split(".")[0]}"("{'", "'.join(attributes)}")')

            # Add quotations to CHAR and VARCHAR types
            for i in range(len(line)):
                if ((types[i] == "CHAR" or types[i] == "VARCHAR") and line[i] != "NULL"):
                    line[i] = f"'{line[i].strip(",").replace("'", "''")}'"

            # Add Values to code
            code_line.append(f"\nVALUES({", ".join(line)});\n")

        # Write code_line to code file
        with open(out_path, "a") as f:
            f.write(f"/* Insert Statements for {out_path.split("\\")[-1].split(".")[0]} */ \n")
            f.write(" ".join(code_line))


# File to create table statement code
def tables(file, out_path, attributes, types, restrictions):
    # Set code line
    code_line = ["CREATE", "TABLE", f'"{out_path.split("\\")[-1].split(".")[0]}"(', "\n"]

    # Iterate through each column
    for i in range(len(types)):
        # Add attribute, type, restriction, and new line to code line
        code_line.append(f'\t"{attributes[i]}" {types[i]}{restrictions[i]},\n')

    # Add ending to file after removing last comma
    code_line[-1] = code_line[-1][:-2] + code_line[-1][-1] # Removes last comma
    code_line.append(");\n\n")

    # Open output file and add to it
    with open(out_path, "a") as f:
        f.write(f"/* Tables for {out_path.split("\\")[-1].split(".")[0]} */\n") # Comment for tables
        f.write(" ".join(code_line)) # Tables


# Main function
def main():
    # Get current working directory and set directory of folder with files
    cwd = os.getcwd()
    directory = "Input"
    out_dir = "Output"

    # Iterate through all files stored in directory folder
    for file in os.listdir(os.path.join(cwd, directory)):
        path = os.path.join(cwd, directory, file)
        out_path = os.path.join(cwd, out_dir, f"{file.split(".")[0]}.sql")

        # Get list of type(s)
        types = get_types(path)

        # Get list of restriction(s)
        restrictions = get_restrictions(path, types)

        # Get attributes
        with open(path, "r") as f:
            attributes = f.readline().strip("\n").split(",")

        # Create file
        with open(out_path, "w"):
            pass

        # Call tables and inserts functions
        tables(path, out_path, attributes, types, restrictions)
        inserts(path, out_path, attributes, types)


# Call main function
main()