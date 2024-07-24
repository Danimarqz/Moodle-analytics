import os
import json
import requests
import pandas as pd
import glob
import logging
from datetime import datetime
from dotenv import load_dotenv
import sys

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def separar():
    try:
        with open(resource_path('nombre_centros.json')) as f:
            nombreCentros = json.load(f)
    except Exception as e:
        logging.error(f"Error loading nombre_centros.json: {e}")

    output_directory = os.path.join(os.path.dirname(sys.executable), "centros")
    current_date = datetime.now().strftime("%d_%m")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    excel_file_path = archivo_destino
    try:
        excel_file = pd.ExcelFile(excel_file_path)
    except Exception as e:
        logging.error(f"Error loading {excel_file_path}: {e}")

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name)
        sheet_name_normalized = sheet_name.lstrip('0')
        nombre = nombreCentros.get(sheet_name_normalized)

        if nombre:
            # Write the DataFrame to a separate Excel file
            output_file = os.path.join(output_directory, f"{sheet_name}_{nombre}_{current_date}.xlsx")
            df.to_excel(output_file, index=False)
            logging.info(f"Saved {sheet_name} to {output_file}")
        else:
            logging.warning(f"Skipping {sheet_name} because no code found in mapping.")

load_dotenv(resource_path('.env'))

try:
    with open(resource_path('nombre_centros.json')) as f:
        nombreCentros = json.load(f)
except Exception as e:
    logging.error(f"Error loading nombre_centros.json: {e}")

nombreCentros_normalized = {k.lstrip('0'): v for k, v in nombreCentros.items()}

try:
    with open(resource_path('onlysavia.json')) as f:
        dict = json.load(f)
except Exception as e:
    logging.error(f"Error loading onlysavia.json: {e}")

dfs = {}
username = os.getenv('CAMPUS_USERNAME')
password = os.getenv('CAMPUS_PASSWORD')
archivo_destino = os.path.join(os.path.dirname(sys.executable), 'Savia Centros.xlsx')
output_directory = os.path.dirname(sys.executable)

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
        logging.error('Login failed. Invalid username or password.')
    else:
        logging.info('Login successful. Initiating file download...' + file_name)
        try:
            file_response = session.get(file_link)
            with open(file_name, 'wb') as file:
                file.write(file_response.content)
            logging.info('File downloaded successfully.')
        except Exception as e:
            logging.error(f"Error downloading file {file_name}: {e}")
        finally:
            session.close()

for key in dict:
    descarga_informe(dict[key]['login'], dict[key]['file'], resource_path(dict[key]['output']))

# Procesar los archivos CSV y convertirlos en un Excel con hojas separadas por centro
try:
    writer = pd.ExcelWriter(os.path.join(output_directory, 'Savia Centros.xlsx'), engine='xlsxwriter')
except Exception as e:
    logging.error(f"Error creating Excel writer: {e}")

for csvfile in glob.glob(resource_path('*.csv')):
    try:
        df = pd.read_csv(csvfile, encoding='utf8')
        if 'Fecha fin' in df.columns:
            df['Fecha fin'] = pd.to_datetime(df['Fecha fin'], dayfirst=True, errors='coerce')
            date = datetime(2024, 1, 1).date()
            logging.info(f"Date filter set to: {date}")
            valid_date_mask = ~df['Fecha fin'].isna() & (df['Fecha fin'].dt.date >= date)
            filtered_df = df[valid_date_mask].copy()
            filtered_df['Centro'] = filtered_df['Centro'].astype(str).str.split('.').str[0] #Pasar los centros a string
            active_filtered_df = filtered_df[filtered_df['F_BAJA'].isna()]  # filtra el df para que se muestren los valores nulos
            active_filtered_df.loc[:, 'Nota Examen final'] = active_filtered_df['Nota Examen final'].str.replace('%', '').astype(float)
            name = os.path.splitext(os.path.basename(csvfile))[0]
            
            grupos = active_filtered_df.groupby('Centro')

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
        logging.error(f"Error processing {csvfile}: {e}")

# Guardar cada DataFrame en una hoja separada del archivo Excel
for centro, df in dfs.items():
    try:
        df.to_excel(writer, sheet_name=centro[:31], index=False)
    except Exception as e:
        logging.error(f"Error writing Excel sheet {centro}: {e}")

try:
    writer.close()  # Usar close() en lugar de save()
except Exception as e:
    logging.error(f"Error closing Excel writer: {e}")

# Eliminar archivos CSV
dir_files = os.listdir(os.getcwd())

for file in dir_files:
    if file.endswith(".csv"):
        try:
            os.remove(file)
            logging.info(f"Archivo {file} eliminado correctamente.")
        except Exception as e:
            logging.error(f"Error removing file {file}: {e}")

separar()
