import pandas as pd

def merge(dfs):
    archivo_destino = 'Savia Centros.xlsx'

    with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)