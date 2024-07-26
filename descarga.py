from datetime import datetime
import logging
import sys
import requests
import os
import glob
import json
import pandas as pd
from dotenv import load_dotenv
from merge import merge

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# URLs
load_dotenv(resource_path('.env'))
with open(resource_path('campus.json')) as f:
    dict = json.load(f)

dfs = {}
username = os.getenv('CAMPUS_USERNAME')
password = os.getenv('CAMPUS_PASSWORD')

login_payload = {
    'username': username,
    'password': password,
}
def descarga_informe(login, file_link, file_name):
    session = requests.Session()
    session.post(login, data=login_payload)

    try:
        file_response = session.get(file_link)
    except:
        print(file_response.status_code)

    with open(file_name, 'wb') as file:
        file.write(file_response.content)
    print('File downloaded successfully.')
    session.close()

for key in dict:
    descarga_informe(dict[key]['login'], dict[key]['file'], dict[key]['output'])

#csv a xlsx
for csvfile in glob.glob(os.path.join(os.path.dirname(sys.executable), '*.csv')):
    try:
        df = pd.read_csv(csvfile, encoding='utf8')
        if 'Fecha fin' in df.columns:
            df['Fecha fin'] = pd.to_datetime(df['Fecha fin'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
            df['Fecha inicio'] = pd.to_datetime(df['Fecha inicio'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
            today = datetime.now().date()
            valid_date_mask = ~df['Fecha fin'].isna() & (df['Fecha fin'].dt.date >= today)
            valid_date_mask_inicio = ~df['Fecha inicio'].isna() & (df['Fecha inicio'].dt.date <= today)
            filtered_df = df[valid_date_mask & valid_date_mask_inicio]
            filtered_df.loc[:,'Nota Examen final'] = filtered_df['Nota Examen final'].str.replace('%', '').astype(float)
            name = os.path.splitext(os.path.basename(csvfile))[0]
            # calculations = {
            #     'Text1': 'Total matriculados',
            #     'Calculation1' : filtered_df['DNI'].count(),
            #     'Text2': 'Iniciados',
            #     'Iniciados': ((filtered_df['Tiempo total de dedicación'] == '00h 00m 00s') | ~filtered_df['Tiempo total de dedicación'].isna()).count(),
            #     'Text3' : 'Pendientes de inicio',
            #     'NoIniciados' : ((filtered_df['Tiempo dedicación Scorms'] == '00h 00m 00s') | ~filtered_df['Tiempo dedicación Scorms'].isna()).count(),
            #     'Text4' : 'Finalizados',
            #     'Finalizados' : (filtered_df['Nota Examen final'] > 0).count(),
            #     'Text5' : 'No finalizados',
            #     'NoFinalizados': (filtered_df['Nota Examen final'] > 0).count() - (((filtered_df['Tiempo total de dedicación'] == '00h 00m 00s') | ~filtered_df['Tiempo total de dedicación'].isna()).count())
            # }
            # percentages = {
            #     '1':'',
            #     '2':'',
            #     'Porcentaje Iniciados / Total Matriculados': (calculations['Iniciados'] / calculations['Total matriculados']) * 100 if calculations['Total matriculados'] != 0 else 0,
            #     '3':'',
            #     'Porcentaje Pendientes de inicio / Iniciados': (calculations['NoIniciados'] / calculations['Iniciados']) * 100 if calculations['Iniciados'] != 0 else 0,
            #     '4':'',
            #     'Porcentaje Finalizados / Iniciados': (calculations['Finalizados'] / calculations['Iniciados']) * 100 if calculations['Iniciados'] != 0 else 0,
            #     '5':'',
            #     'Porcentaje NoFinalizados / Iniciados': (calculations['NoFinalizados'] / calculations['Iniciados']) * 100 if calculations['Iniciados'] != 0 else 0,
            # }
            
            # calculations_df = pd.DataFrame([calculations])
            # percentages_df = pd.DataFrame([percentages])

            # filtered_df = pd.concat([calculations_df, percentages_df], ignore_index=True)
            dfs[name] = filtered_df
        else:
            name = os.path.splitext(os.path.basename(csvfile))[0]
            dfs[name] = df
    except Exception as e:
        print(f"Error processing {csvfile}: {e}")

#delete csv
dir = os.getcwd()

dir_files = os.listdir(dir)

for file in dir_files:
    if file.endswith(".csv"):
        ruta_completa = os.path.join(dir, file)
        os.remove(ruta_completa)
        print(f"Archivo {file} eliminado correctamente.")

merge(dfs)