from pathlib import Path
import pypdf
import pandas as pd

#directory location
script_dir = Path(__file__).resolve().parent

#Input and Output paths
pdf_path = script_dir / "Data" / "BLM Herd Area and Herd Management Area Statistics.pdf"
output_excel_path = script_dir / "Data" / "Final_Cleaned_Population_Data.xlsx"
output_csv_path = script_dir / "Data" / "Final_Cleaned_Population_Data.csv"

print(f"Reading PDF summary from: {pdf_path}")

#Open PDF and read Page 1
reader = pypdf.PdfReader(pdf_path)
page1_text = reader.pages[0].extract_text()

#Parse state rows
states_data = []
target_states = ["AZ", "CA", "CO", "ID", "MT", "NV", "NM", "OR", "UT", "WY"]

for line in page1_text.split("\n"):
    parts = line.strip().split()
    if parts and parts[0] in target_states:
        state = parts[0]
        try:
            horses = int(parts[6].replace(",", ""))
            burros = int(parts[7].replace(",", ""))
            total_pop = int(parts[8].replace(",", ""))

            if total_pop > 0:
                states_data.append({
                    "State": state,
                    "Horses": horses,
                    "Burros": burros,
                    "Total Population": total_pop
                })
        except (ValueError, IndexError):
            continue

df_population = pd.DataFrame(states_data)

print("\nSTATES WITH ACTIVE POPULATIONS")
print(df_population.to_string(index=False))

#Save cleaned data to the Data folder
df_population.to_excel(output_excel_path, index=False)
df_population.to_csv(output_csv_path, index=False)

print("\nCleaned population data successfully saved to Final_Cleaned_Population_Data.xlsx!")