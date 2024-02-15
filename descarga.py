from datetime import datetime
import requests
import os
import glob
import json
import pandas as pd
from dotenv import load_dotenv
from merge import merge

# URLs
load_dotenv()
with open('campus.json') as f:
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
    login_response = session.post(login, data=login_payload)

    if 'Invalid login' in login_response.text:
        print('Login failed. Invalid username or password.')
    else:
        print('Login successful. Initiating file download...' + file_name)
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
for csvfile in glob.glob(os.path.join('.','*.csv')):
    try:
        df = pd.read_csv(csvfile, encoding='utf8')
        if 'Fecha fin' in df.columns:
            df['Fecha fin'] = pd.to_datetime(df['Fecha fin'], format='%d/%m/%Y', errors='coerce')
            today = datetime.now().date()
            valid_date_mask = ~df['Fecha fin'].isna() & (df['Fecha fin'].dt.date >= today)
            filtered_df = df[valid_date_mask]
            filtered_df.loc[:,'Fecha fin'] = filtered_df['Fecha fin'].dt.strftime('%d/%m/%Y')
            filtered_df.loc[:,'Nota Examen final'] = filtered_df['Nota Examen final'].str.replace('%', '').astype(float)
            name = os.path.splitext(os.path.basename(csvfile))[0]
            grupos = filtered_df.groupby('Centro')

            for centro, grupo in grupos:
                dfs[centro] = grupo
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