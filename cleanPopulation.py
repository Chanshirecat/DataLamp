import pandas as pd

# Specify the path to the Excel file
excel_file_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Herd Area and Herd Management Area Statistics.xlsx"

# Load the data from the Excel file
population_df = pd.read_excel(excel_file_path)

# Print the number of columns in the dataframe to diagnose the issue
print(f"Number of columns: {len(population_df.columns)}")

# Check the column names
print(f"Columns: {population_df.columns.tolist()}")

# Modify the column names to match the dataframe structure (adjusted to 13 columns)
# Example: You can modify the column names to reflect your dataset. Here's an example assuming your dataset has 13 columns.
population_df.columns = ['State', 'BLM Acres', 'Total Acres', 'BLM Acres from BLM',
                         'Total Acres from BLM', 'Horses', 'Burros', 'Total Population',
                         'High AML', 'Extra Column 1', 'Extra Column 2', 'Extra Column 3', 'Extra Column 4']

# Output the first few rows of the dataframe to verify the changes
print(population_df.head())
