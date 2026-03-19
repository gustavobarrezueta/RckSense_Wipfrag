#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 05 15:23:39 2024

@author: ggj
"""


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

pio.renderers.default='browser'
mpl.rcParams['agg.path.chunksize'] = 10000


na_list = ['Invalid Data',
               'Calc Failed', 
               "No Data",
               "Error",
               "Bad",
               "Pt Created", 
               'Scan Off', 
               'I/O Timeout',
               '#VALUE!', 
               '#DIV/0!', 
               '[-11059] No Good Data For Calculation', 
               'Tag not found', 
               'Configure',
               'SM',
               'planta detenida',
               'sin muestra', 
               'Invalid function argument:Start time and End time differ by less than 15 micro seconds', 
               '[-11101] All data events are filtered in summary calculation', 
               'Calculation aborted', 
               'Argument is not a string or cell reference', 
               'Shutdown',
               'snapfix',
               'Bad Input',
               'Intf Shut',
               'Argument is not a string or cell reference',
               'Out of Serv',
               'Not Connect',
               'Under Range',
               'Over Range',
               'Blank Tagname',
               'El valor de DateTime especificado representa una hora no válida. Por ejemplo, cuando el reloj se adelanta, todas las horas del período que se omite no son válidas._x000D_\nNombre del parámetro: dateTime',
               'Comm Fail',
               'AccessDenied' #Eliminar eventualmente si es que no migran los tags
               ]



def leer_archivos(archivo, path, nombre_hoja, type_file):
    try:
        df = pd.read_pickle(path + archivo+ '_{}'.format(nombre_hoja) +".pkl")
        print("lectura exitosa de pkl")
        
    except:
        if type_file == 'excel':
            print("no se encontró archivo plk así que se leerá excel")
            df = pd.read_excel(path + archivo+".xlsx", sheet_name = nombre_hoja)
        elif type_file == 'csv':
            print("no se encontró archivo plk así que se leerá csv")
            df = pd.read_csv(path + archivo+".csv")
        df.to_pickle(path+ archivo +'_{}'.format(nombre_hoja)+'.pkl')
        print('Lectura exitosa de archivo')
    
    return df


def leer_archivos2(archivo, path, nombre_hoja):
    df = pd.read_excel(path + archivo+".xlsx", sheet_name = nombre_hoja, na_values = na_list)
    df.to_pickle(path+ archivo +'.pkl')
    print('Lectura exitosa de excel')
    
    return df



def remove_outliers(df, columns):
    for col in columns:
       
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


    return df

def binning(dataframe, columna, bins, columnas_seleccionadas, calcular='media'):
    """
    Calcula estadísticas (media o máximo) de columnas seleccionadas en un DataFrame agrupado por intervalos de otra columna.
    
    Parámetros:
        dataframe (pandas.DataFrame): El DataFrame que contiene los datos.
        columna (str): El nombre de la columna utilizada para definir los intervalos.
        bins (array_like): Los intervalos utilizados para agrupar los datos.
        columnas_seleccionadas (list): Lista de columnas en las que calcular las estadísticas.
        calcular (str, opcional): La estadística a calcular ('media' o 'maximo'). Por defecto, 'media'.
    
    Retorna:
        pandas.DataFrame: Un DataFrame que contiene las estadísticas de las columnas seleccionadas y el conteo de observaciones por intervalo.
    """
    # Agrupar los datos por intervalo
    agrupado = pd.cut(dataframe[columna], bins=bins)
    
    # Seleccionar la función de agregación
    if calcular == 'media':
        funcion_agregacion = 'mean'
    elif calcular == 'maximo':
        funcion_agregacion = 'max'
    else:
        raise ValueError("El parámetro 'calcular' debe ser 'media' o 'maximo'.")
    
    # Calcular las estadísticas de las columnas seleccionadas y el conteo de observaciones por intervalo
    estadisticas = dataframe.groupby(agrupado)[columnas_seleccionadas].agg(funcion_agregacion)
    conteo = dataframe.groupby(agrupado).size()
    
    # Concatenar los resultados en un DataFrame
    resultado = pd.concat([estadisticas, conteo], axis=1)
    
    # Renombrar las columnas
    nombre_estadistica = 'Mean' if calcular == 'media' else 'Max'
    resultado.columns = [f'{nombre_estadistica} {col}' for col in estadisticas.columns] + ['Count']
    
    # Eliminar filas con valores NaN
    resultado = resultado.dropna()
    
    return resultado



def nan_to_mean(df, columnas):
    """
    Convierte los valores de las columnas especificadas a numéricos y rellena NaN con la media de la columna.
    
    Args:
    df (pd.DataFrame): El DataFrame a procesar.
    columnas (list): Lista de nombres de las columnas a procesar.
    
    Returns:
    pd.DataFrame: El DataFrame con las columnas procesadas.
    """
    for col in columnas:
        # Convertir los valores de la columna a numéricos, coercionando errores a NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Rellenar NaN con la media de la columna
        df[col] = df[col].fillna(value=df[col].mean())
    
    return df


def grafico_caja_bigotes(dataframe, columns, labels):
    """
    Crea un gráfico de caja y bigotes para una columna específica de un DataFrame.
    
    Args:
    dataframe (pd.DataFrame): El DataFrame que contiene los datos.
    columns (list): Lista de nombres de las columnas a graficar.
    labels (list): Lista de etiquetas para las columnas.

    Returns:
    fig, axs: Figura y ejes del gráfico.
    """
    # Aplicar el estilo de Seaborn
    sns.set(style="whitegrid")

    fig, axs = plt.subplots(len(columns), 2, figsize=(40, 30))

    # Gráficos de línea
    colors = ['C9', 'C0', 'C3', 'C5', 'C3', 'C3']

    for i, (col, label, color) in enumerate(zip(columns, labels, colors)):
        axs[i, 0].plot(dataframe[col], color, linewidth=1, label=label)
        axs[i, 0].set_ylabel(label, fontsize=20)
        axs[i, 0].legend(loc='upper right', fontsize=16)
        axs[i, 0].grid(True)
        axs[i, 0].set_title(f'Gráfico de {label}', fontsize=24)

    # Gráficos de caja
    for i, (col, label) in enumerate(zip(columns, labels)):
        axs[i, 1].boxplot(dataframe[col])
        axs[i, 1].set_ylabel(label, fontsize=20)
        axs[i, 1].set_title(f'Boxplot de {label}', fontsize=24)
        axs[i, 1].grid(True)

    # Títulos y etiquetas generales
    fig.suptitle('Análisis de Variables', fontsize=32)
    fig.tight_layout(rect=[0, 0, 1, 0.96])  # Ajusta para que no se solapen los títulos

    # Etiquetas comunes para los ejes X
    for ax in axs[-1, :]:
        ax.set_xlabel('Índice', fontsize=20)

    return fig, axs