import pandas as pd

def merge(dfs, sheet_names):
    archivo_destino = 'Informe completo.xlsx'

    with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
        for sheet_name, df in zip(sheet_names, dfs):
            df.to_excel(writer, sheet_name=sheet_name, index=False)