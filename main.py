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

            # Iterate through each character in cell and check if all are valid
            for character in cell:
                # If a character is not in the valid list, the type is not CHAR
                if (character not in valid_char_letters or (col_type != "CHAR" and col_type != "NULL")):
                    col_type = "VARCHAR"
                    break

            # If you can convert the type to INT or FLOAT (DEC), it is not VARCHAR or CHAR
            try:
                cell = float(cell)
                if (col_type == "CHAR"):
                    col_type = "VARCHAR"
                    break
                elif (cell // 1 == cell):
                    col_type = "INT"
                else:
                    col_type = "DEC"
            except ValueError:
                # If type is CHAR, keep going
                if (col_type == "NULL" or col_type == "CHAR"):
                    col_type = "CHAR"

                # Else it is VARCHAR, stop
                else:
                    col_type = "VARCHAR"
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
                restrictions.append(char_restr(col))
            elif (types[i] == "DEC"):
                restrictions.append(dec_restr(col))
            else:
                restrictions.append("")

        # Return list of restrictions
        return restrictions


# Function for char & varchar
def char_restr(col):
    # Initially set max_len to zero
    max_len = 0

    # Iterate through each instance and find the max_len
    for inst in col:
        if (len(inst) > max_len):
            max_len = len(inst)

    # Return the length of the longest instance
    return max_len


# Function for dec
def dec_restr(col):
    # Initially set max precision and max scale to zero
    max_prec = 0
    max_scale = 0

    # Iterate through each instance in column
    for inst in col:
        # Split between decimal point
        number = inst.split(".")

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
def inserts(file):
    # Open file
    with open(file, "r") as f:
        # Get first line for attributes
        attributes = f.readline().strip("\n").split(",")

        # Iterate for each line (except the first one) in file
        for line in f:
            line = line.strip("\n").split(",")


# File to create table statement code
def tables(file):
    # Get list of type(s)
    types = get_types(file)

    # Get list of restriction(s)
    restrictions = get_restrictions(file, types)

    # TEST
    print(types)
    print(restrictions)


# Main function
def main():
    # Get current working directory and set directory of folder with files
    cwd = os.getcwd()
    directory = "Files"

    # Iterate through all files stored in directory folder
    for file in os.listdir(os.path.join(cwd, directory)):
        path = os.path.join(cwd, directory, file)

        # Call tables and inserts functions
        tables(path)
        inserts(path)


# Call main function
main()