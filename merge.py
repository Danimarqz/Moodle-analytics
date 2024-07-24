import os
import sys
import pandas as pd

def merge(dfs):
    archivo_destino = os.path.join(os.path.dirname(sys.executable), 'Informe completo.xlsx')

    with pd.ExcelWriter(archivo_destino, engine='xlsxwriter') as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)