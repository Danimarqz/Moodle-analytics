import json
import os
import pandas as pd
from datetime import datetime

def separate(output_directory, json, archivo_objetivo):
    with open() as f:
        nombreCentros = json.load(f)
    current_date = datetime.now().strftime("%d_%m")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    excel_file = pd.ExcelFile(archivo_objetivo)

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name)
        sheet_name_normalized = sheet_name.lstrip('0')
        nombre = nombreCentros.get(sheet_name_normalized)
        
        if nombre:
            # Write the DataFrame to a separate Excel file
            output_file = os.path.join(output_directory, f"{sheet_name}_{nombre}_{current_date}.xlsx")
            df.to_excel(output_file, index=False)
            print(f"Saved {sheet_name} to {output_file}")
        else:
            print(f"Skipping {sheet_name} because no code found in mapping.")
