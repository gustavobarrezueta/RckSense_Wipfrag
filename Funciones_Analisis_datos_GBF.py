import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import datetime as dt
from datetime import timedelta
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import seaborn as sns
import matplotlib as mpl
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image


def leer_archivos(archivo, path, nombre_hoja, type_file):
    try:
        df = pd.read_pickle(path + archivo+ ".pkl")
        print("lectura exitosa de pkl")
        
    except:
        if type_file == 'excel':
            print("no se encontró archivo plk así que se leerá excel")
            df = pd.read_excel(path + archivo+".xlsx", sheet_name = nombre_hoja)
            df.to_pickle(path+ archivo +'_{}'.format(nombre_hoja)+'.pkl')
        elif type_file == 'csv':
            print("no se encontró archivo plk así que se leerá csv")
            df = pd.read_csv(path + archivo+".csv")
            df.to_pickle(path + archivo + '.pkl')
        print('Lectura exitosa de archivo')
    
    return df


def plot_variables(dataframe, columns, save=False):

    labels = columns

    # Aplicar el estilo de Seaborn
    sns.set(style="whitegrid")

    fig, axs = plt.subplots(len(columns), 1, figsize=(40, 30))
    # Gráficos de línea
    colors = ['C9', 'C8', 'C7', 'C6', 'C5', 'C4', 'C3', 'C2', 'C1', 'C0', 'm', 'y', 'C9', 'C8', 'C7']
    
    for i, (col, label, color) in enumerate(zip(columns, labels, colors)):
            axs[i].scatter(dataframe.index, dataframe[col], color=color, linewidth=1, label=label)
            axs[i].set_ylabel(label, fontsize=20)
            axs[i].legend(loc='upper right', fontsize=16)
            axs[i].grid(True)
            axs[i].set_title(f'Gráfico de {label}', fontsize=24)


    # Títulos y etiquetas generales
    fig.suptitle('Análisis de Variables', fontsize=32)
    fig.tight_layout(rect=[0, 0, 1, 0.96])  # Ajusta para que no se solapen los títulos
        
    plt.show()
    # Guardar la figura
    if save:
        plt.savefig(f'Plots/Raw_variables.png')

    return "Ploteo de variables exitoso"


def plot_individual_dist(series: pd.Series, columns, bins: int = 50):
        
        series_copy = series.copy()
        series_copy = series_copy.dropna()
        
        for column in columns:
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))

            # Histograma
            axes[0].hist(series_copy[column], bins=bins, density=True, alpha=0.7)
            axes[0].set_title(f'Histograma – {column}')
            axes[0].set_xlabel('Valor')
            axes[0].set_ylabel('Densidad')

            # Boxplot
            axes[1].boxplot(series_copy[column], vert=False)
            axes[1].set_title(f'Boxplot – {column}')

            plt.tight_layout()
            plt.show()

        return 

def replace_strings_with_nan(df, column, string_list):
    
    df[column] = df[column].replace(string_list, np.nan)
    
    return df


def filtrar_bollinger(df, columns, window, parameters):

    num_std_UB = parameters['num_std_UB']
    num_std_LB = parameters['num_std_LB']
    upper_limit_bolli = parameters['upper_limit_bolli']
    down_limit_bolli = parameters['down_limit_bolli']
    
    for column in columns:
        df_copy = df.copy()
        
        df_copy['Bollinger Mean '+f'{column}'] = df_copy[column].rolling(window=window).mean()
        df_copy['Bollinger SD '+f'{column}'] = df_copy[column].rolling(window=window).std()

        df_copy['Bollinger UB '+ f'{column}'] = df_copy['Bollinger Mean '+f'{column}'] + num_std_UB * df_copy['Bollinger SD '+f'{column}']
        df_copy['Bollinger LB ' + f'{column}'] = df_copy['Bollinger Mean '+f'{column}'] - num_std_LB * df_copy['Bollinger SD '+f'{column}']

        if upper_limit_bolli:
            df_copy = df_copy[df_copy[column] <= df_copy['Bollinger UB ' + f'{column}']]
        if down_limit_bolli:
            df_copy = df_copy[df_copy[column] >= df_copy['Bollinger LB ' + f'{column}']]
    
    
    return df_copy

def preprocesamiento_datos(df, sag, columns_rename, time_format='%d-%m-%Y %H:%M:%S'):


    print(f"Procesando {sag}")

    df_copy = df.copy()
    df_copy = df_copy.rename(columns=columns_rename)

    df_copy = df_copy.drop('Unnamed: 0', axis=1)
    
    df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], format=time_format)
    df_copy = df_copy.set_index(pd.DatetimeIndex(df_copy['timestamp']))

    # Deleting duplicate rows
    before_duplicate_drop = len(df_copy.index)
    df_copy.drop_duplicates(inplace=True)
    after_duplicate_drop = len(df_copy.index)
    print("Diferencia de valores nulos antes y después de eliminar duplicados:")
    print(before_duplicate_drop - after_duplicate_drop)

    # Deleting null values
    # before_null_drop = df_copy.isnull().sum()
    # df_copy = df_copy.dropna()
    # after_null_drop = df_copy.isnull().sum()
    # print("Diferencia de valores nulos antes y después de dropna():")
    # print(before_null_drop - after_null_drop)


    return df_copy


def buscar_valores_no_numericos(df, columna):

    mascara_no_numericos = pd.to_numeric(df[columna], errors='coerce').isna()#& df[columna].notna()
    valores_no_numericos = df[mascara_no_numericos][columna]

    print(f"Valores en '{columna}' que no pueden convertirse a número:")
    print(f"Total encontrados: {len(valores_no_numericos)}")
    print(valores_no_numericos.to_string())

    return valores_no_numericos