from datetime import datetime
import requests
import os
import glob
import json
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Leer el archivo JSON con la información de los centros
with open('codigo_centros.json') as f:
    nombreCentros = json.load(f)

# Normalizar los nombres de los centros (eliminar ceros a la izquierda)
nombreCentros_normalized = {k.lstrip('0'): v for k, v in nombreCentros.items()}

# Leer el archivo JSON con las URLs de los informes
with open('onlysavia.json') as f:
    dict = json.load(f)

# Configuración inicial
dfs = {}
username = os.getenv('CAMPUS_USERNAME')
password = os.getenv('CAMPUS_PASSWORD')
archivo_destino = 'Savia Centros.xlsx'
output_directory = os.getcwd()

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

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
            with open(file_name, 'wb') as file:
                file.write(file_response.content)
            print('File downloaded successfully.')
        except Exception as e:
            print(f"Error downloading file {file_name}: {e}")
        finally:
            session.close()

for key in dict:
    descarga_informe(dict[key]['login'], dict[key]['file'], dict[key]['output'])

# Procesar los archivos CSV y convertirlos en un Excel con hojas separadas por centro
writer = pd.ExcelWriter(os.path.join(output_directory, archivo_destino), engine='xlsxwriter')

for csvfile in glob.glob(os.path.join('.', '*.csv')):
    try:
        df = pd.read_csv(csvfile, encoding='utf8')
        if 'Fecha fin' in df.columns:
            df['Fecha fin'] = pd.to_datetime(df['Fecha fin'], format='%d/%m/%Y', errors='coerce')
            today = datetime.now().date()
            valid_date_mask = ~df['Fecha fin'].isna() & (df['Fecha fin'].dt.date >= today)
            filtered_df = df[valid_date_mask].copy()  # Hacer una copia explícita del DataFrame filtrado
            filtered_df.loc[:, 'Fecha fin'] = filtered_df['Fecha fin'].dt.strftime('%d/%m/%Y')
            filtered_df.loc[:, 'Nota Examen final'] = filtered_df['Nota Examen final'].str.replace('%', '').astype(float)
            name = os.path.splitext(os.path.basename(csvfile))[0]
            grupos = filtered_df.groupby('Centro')

            for centro, grupo in grupos:
                # Quita los 0
                centro_sin0 = centro.lstrip('0')
                # Añade los 0
                codigo_centro = '000' + centro_sin0
                grupo['Centro'] = codigo_centro
                if codigo_centro in dfs:
                    dfs[codigo_centro] = pd.concat([dfs[codigo_centro], grupo], ignore_index=True)
                else:
                    dfs[codigo_centro] = grupo
        else:
            name = os.path.splitext(os.path.basename(csvfile))[0]
            dfs[name] = df
    except Exception as e:
        print(f"Error processing {csvfile}: {e}")

# Guardar cada DataFrame en una hoja separada del archivo Excel
for centro, df in dfs.items():
    df.to_excel(writer, sheet_name=centro[:31], index=False)

writer.close()  # Usar close() en lugar de save()

# Eliminar archivos CSV
dir_files = os.listdir(os.getcwd())

for file in dir_files:
    if file.endswith(".csv"):
        os.remove(file)
        print(f"Archivo {file} eliminado correctamente.")
