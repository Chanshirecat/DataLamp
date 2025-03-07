import pandas as pd

# path to the Excel file
excel_file_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Herd Area and Herd Management Area Statistics.xlsx"

# loads the Excel file and skips the metadata rows
df_population = pd.read_excel(excel_file_path, skiprows=2)

# renames the relevant columns
df_population = df_population.rename(columns={
    "Unnamed: 0": "State",
    "Estimated Populations": "Horses",
    "Unnamed: 9": "Burros",
    "Unnamed: 10": "Total Population"
})

# selects only relevant columns
df_population = df_population[["State", "Horses", "Burros", "Total Population"]]

# removes irrelevant rows
df_population = df_population.dropna(subset=["State"])
df_population = df_population[~df_population["State"].str.contains("TOTAL|March", na=False)]

# converts the population columns to numeric values by removing commas
df_population["Horses"] = df_population["Horses"].astype(str).str.replace(",", "").astype(float).astype(int)
df_population["Burros"] = df_population["Burros"].astype(str).str.replace(",", "").astype(float).astype(int)
df_population["Total Population"] = df_population["Total Population"].astype(str).str.replace(",", "").astype(float).astype(int)

# saves the cleaned data to new CSV and Excel file
cleaned_csv_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"
cleaned_excel_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.xlsx"

df_population.to_csv(cleaned_csv_path, index=False)
df_population.to_excel(cleaned_excel_path, index=False)

# prints the cleaned data
print("Cleaned population data successfully saved!")
print(df_population.head())
