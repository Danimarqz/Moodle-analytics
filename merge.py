import glob
import os
import pandas as pd

archivo_destino = 'Informe completo.xlsx'

dfs = {}

for file in glob.glob(os.path.join('.','*.xlsx')):
    if file != archivo_destino:
        sheet_name = os.path.basename(file).split('/')[-1].split('.')[0]
        df = pd.read_excel(file, engine="openpyxl")
        dfs[sheet_name] = df

#TODO filter df - enddate > today
# summarize data in the first 8 rows

with pd.ExcelWriter(archivo_destino, engine='openpyxl') as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, startrow=8, index=False)