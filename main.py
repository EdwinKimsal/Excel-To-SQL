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
        col_type = "CHAR"
        for j in range(rows):

            # Create lowercase variable of cell
            cell = cells[i + j*columns].lower()

            # Iterate through each character in cell and check if all are valid
            for character in cell:
                # If a character is not in the valid list, the type is not CHAR
                if (character not in valid_char_letters or col_type != "CHAR"):
                    col_type = "VARCHAR"
                    break

            # If you can convert the type to INT or FLOAT (DEC), it is not VARCHAR or CHAR
            try:
                int(cell)
                col_type = "INT"
            except ValueError:
                try:
                    float(cell)
                    col_type = "FLOAT"
                except ValueError:
                    # If type is CHAR, keep going
                    if (col_type == "CHAR"):
                        pass

                    # Else it is VARCHAR, stop
                    else:
                        col_type = "VARCHAR"
                        break

        # Append column type
        types.append(col_type)

    # Return list of types
    return types


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
    print(types)

    # Get list of restriction(s)



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