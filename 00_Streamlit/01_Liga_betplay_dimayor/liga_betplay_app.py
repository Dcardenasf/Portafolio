import pandas as pd
import streamlit as st
import requests
import io
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from pathlib import Path

base_dir = Path(__file__).resolve().parent

st.set_page_config(layout="wide")

with st.container(horizontal=True, horizontal_alignment="right", border=True):
    st.image(f"{base_dir}/liga-betplay-dimayor.png", width=80)
    st.title("Análisis Exploratorio de Datos de la Liga BetPlay Dimayor 2023-2026 ")

sns.set_theme(style="whitegrid", palette="viridis")


st.markdown("""
## 📝️00_Preliminares.

**Dataset:** Tabla de estadísticas tomada de [FBREF](https://fbref.com/en/comps/41/stats/Primera-A-Stats)

**Objetivo Analítico:** Identificar patrones de comportamiento que afecten el rendimiento de los jugadores de la **Liga Betplay Dimayor** entre los años 2023 y 2026.

---

## 🧐️ 01_Comprensión de los datos.

Se cargan archivos `CSV` individuales por cada años desde el 2023 hasta el 2026(oct), con la información estadística de cada uno de los jugadores de la **Liga Betplay Dimayor**

### Datos básicos

Variable|Descripción|Tipo de dato
:---|:---|:---
Rk|Rango (Rank) Este es un conteo de las filas de arriba hacia abajo.Se recalcula después de ordenar una columna.|Integer
Player|Nombre del jugador|String    
Nation|Nacionalidad del jugador. Primero, verificamos nuestros registros en partidos internacionales a nivel absoluto (selección mayor).Luego a nivel juvenil.Después, la ciudadanía presentada en Wikipedia.Finalmente, usamos su lugar de nacimiento cuando está disponible.|String
Pos|Posición, Posición que el jugador desempeña con más frecuencia: `GK` -Porteros, `DF` - Defensas, `MF` - Mediocampistas, `FW` - Delanteros|String
Squad|Equipo al cual pertenece|String
Age|Edad al inicio de la temporada Se calcula al 1 de agosto para las ligas de invierno y al 1 de febrero para las ligas de verano.|Integer
Born|Año de nacimiento|Integer                                                
                             
                                           
### Tiempo de Juego                                         
                                                                            
Variable|Descripción|Tipo de dato
:---|:---|:---
MP|Partidos Jugados Partidos jugados por el jugador o el equipo.|Integer                  
Starts|Titularidades Partido o partidos iniciados por el jugador como titular.|Integer                  
Min|Minutos jugados|Integer
90s|Fracciones de 90 minutos jugados Minutos totales jugados divididos por 90.|Float64
                                                                            
### Rendimiento 
Variable|Descripción|Tipo de dato
:---|:---|:---
Gls|Goles, Goles marcados o permitidos.|Integer                                               
Ast|Asistencias|Integer
G+A|Participaciones en goles|Integer                       
G-PK|Goles sin contar penaltis (Goles de jugada)|Integer                      
PK|Tiros de penalti marcados|Integer                                      
PKatt|Tiros de penalti intentados|Integer                                     
CrdY|Tarjetas Amarillas|Integer                                              
CrdR|Tarjetas Rojas|Integer                     
Gls.1|Goles marcados cada 90 minutos|Float64
Ast.1|Asistencias dadas cada 90 minutos|Float64
G+A.1|Participaciones en gol cada 90 minutos|Float64
""")

st.sidebar.header("Filtros")
temporada_filtro = st.sidebar.selectbox(
    'Temporada', list(reversed(range(2023, 2027))))


# 

@st.cache_data
def cargar_datos(temp):
    url = f"{base_dir}/data/{temp}.csv"
    try:
        df = pd.read_csv(url)
        df = df.drop(columns={'G-PK.1', 'G+A-PK', 'Matches', '-9999'})
        df['Age'] = temp-df.Born
        df['Nation'] = df['Nation'].str[3:]
        df['Pos'] = df['Pos'].str[:2]
        return df
    except Exception as e:
        st.error(f"Se genero un error al cargar los datos: {e}")
        return None


df = cargar_datos(temporada_filtro)


df_nulos = df.copy()
cantidad = len(df_nulos)
nulos = df_nulos.isna().sum().sum()
df_nulos= df_nulos.isna().sum().reset_index(name='Cantidad de nulos')
df_nulos['Porcentaje de nulos']=(df_nulos['Cantidad de nulos']/cantidad).map("{:.2%}".format)
df_nulos.columns=['Variable','Cantidad de nulos','Porcentaje de nulos']
df_nulos=df_nulos[df_nulos['Cantidad de nulos']>0]
st.write(f'EL conjunto de datos de la {temporada_filtro}, cuenta con {cantidad} observaciones de los cuales hay {nulos} valores faltantes, distribuidos en {df_nulos.shape[0]} variables:')
st.dataframe(df_nulos,hide_index=True)
df = df.dropna()
st.write(f'Ahora bien, luego de aplicar la limpieza de registros faltante `dropna()`, el dataset se redujo a {len(df)} observaciones,¿Por qué se eliminan {cantidad-len(df)} filas en lugar de {nulos} ? esto se debe a la coexistencia de nulos, es decir que una observación puede tener 1 o varios datos faltantes.')

def evaluar_calidad(porcentaje_limpio):
    if porcentaje_limpio >=0.95:
        return '🟢️ Buena'
    elif porcentaje_limpio < 0.95 and porcentaje_limpio >= 0.75:
        return '🟡️ Intermedio'
    else:
        return '🔴️ Mala'

porcentaje_limpio = (len(df)/cantidad)
calidad = evaluar_calidad(porcentaje_limpio)

st.metric(label=f'Calidad de los datos: {calidad}',value=f'{porcentaje_limpio:.2%} ',delta=f'{porcentaje_limpio-1.0:.2%}',border=True)

st.header(f"02_Análisis de la temporada {temporada_filtro}",icon='📊️')
st.subheader("Análisis univariado")

#Agrupar por edades

bins_edades = [0,20,25,30,35,100] # Mejor colocar un 0 al iniciar
etiquetas_edades = ['Menores de 20','20-25','25-30','30-35','Mayores de 35'] # las etiquetas deben ser menos que los cortes (bins)

df_edades = df.copy()
df_edades['Rango edad'] = pd.cut(df_edades['Age'],bins=bins_edades, labels=etiquetas_edades,right=False)

#distribución por edades
col_1, col_2 = st.columns(2)

with col_1:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.countplot(data=df_edades, x="Rango edad", ax=ax)
    ax.bar_label(ax.containers[0])
    ax.set_ylabel('Cantidad')
    ax.set_title("Distribución por rango de edad")
    plt.tight_layout()
    st.pyplot(fig)

    promedio_edad = round(df_edades['Age'].mean(),1)
    concentracion = df_edades['Rango edad'].value_counts()
    cantidad_concentracion = concentracion.max()
    categoria_concentracion = concentracion.idxmax()


    st.warning(f'La edad de los jugadores se concentra entre los **{categoria_concentracion}** años con **{cantidad_concentracion}** observaciones y el promedio de edad de los jugadores es de **{promedio_edad}** años.',icon='🔍️')

#

with col_2:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(data=df_edades, x="Min", ax=ax)
    ax.bar_label(ax.containers[0])
    ax.set_ylabel('Cantidad')
    ax.set_title("Minutos jugados por jugador")
    plt.tight_layout()
    st.pyplot(fig)

    promedio_minutos = round(df_edades['Min'].mean(),1)
    promedio_noventa = round(promedio_minutos/90,1)


    st.warning(f'Los jugadores juegan en promedio **{promedio_minutos}** minutos, es decir **{promedio_noventa}** partidos durante el año.',icon='🔍️')

st.subheader('Análisis Bivariado') 

st.write(f'Para los siguientes análisis no se tienen en cuenta los porteros `GK`, los jugadores que se destacan son aquellos a los que el aportan más de 0.7 participaciones cada 90 minutos.')

df_edades['Jugador_destacado'] = df_edades['G+A.1']>0.7
df_edades=df_edades[df_edades['Pos']!='GK']

col_1, col_2 = st.columns(2)

with col_1:

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=df_edades, x="Min",y='G+A',hue='Jugador_destacado', ax=ax, palette= {True:'g',False:'r'})
    ax.set_title("¿Influye el tiempo de juego para aportar más en goles?")
    ax.set_ylabel('Aporte en goles')    
    ax.set_xlabel('Minutos Jugados')    
    plt.tight_layout()
    st.pyplot(fig)
    st.success(f'El tiempo de juego si influye, a mayor tiempo de juego más aportes a goles.',icon='🔍️')

with col_2:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=df_edades, x="Rango edad",y='G+A.1', ax=ax,errorbar=None,estimator='mean')
    ax.set_title("¿Los jugadores mayores a 30 aportan más oportunidades de gol que los menores a 30?")
    ax.set_ylabel('Aporte en goles')    
    ax.set_xlabel('Rango de edad')
    ax.bar_label(ax.containers[0])    
    plt.tight_layout()
    st.pyplot(fig)
    df_edades['Mayor a 30'] = df_edades['Age']>=30
    participaciones_edad = pd.pivot_table(df_edades,values='G+A.1',columns='Mayor a 30',aggfunc='mean').reset_index()
    if participaciones_edad[True].iloc[0] > participaciones_edad[False].iloc[0]:
        mensaje = "Los Jugadores mayores a 30, **si** aportan más participaciones de gol que los jugadores menores a 30 años."
    else:
        mensaje = "Los Jugadores mayores a 30, **no** aportan más participaciones de gol que los jugadores menores a 30 años."
    st.success(mensaje,icon='🔍️')

#col_numerica = df_edades.select_dtypes(include=["number"])
#fig=sns.pairplot(df_edades,hue='Jugador_destacado')
#st.pyplot(fig)
   

st.header('03_Dashboard interactivo',icon='⚽️')

st.write('Acá puedes interactuar con la sección de filtros por tu equipo favorito o por alguna posición.')

# Filtro de equipos

equipos = sorted(df.Squad.unique())
equipo_filtro = st.sidebar.multiselect('Equipo', equipos, equipos)

# Filtro de posición

posicion = sorted(df.Pos.unique())
posicion_filtro = st.sidebar.multiselect('Posición', posicion, posicion)

df_filtrado = df[(df.Squad.isin(equipo_filtro) &
                  (df.Pos.isin(posicion_filtro)))]

if df_filtrado.empty:
    st.warning(
        "Por favor selecciona al menos un equipo y una posición para visualizar los datos", icon="⚠️")
else:
    # Goleador
    max_goles_id = df_filtrado['Gls'].idxmax()
    goleador = df_filtrado.loc[max_goles_id, 'Player']
    cantidad_goles = df_filtrado.loc[max_goles_id, 'Gls']
    equipo_goleador = df_filtrado.loc[max_goles_id, 'Squad']

    # Asistencias
    max_asistencias_id = df_filtrado['Ast'].idxmax()
    asistencias = df_filtrado.loc[max_asistencias_id, 'Player']
    cantidad_asistencias = df_filtrado.loc[max_asistencias_id, 'Ast']
    equipo_asistencia = df_filtrado.loc[max_asistencias_id, 'Squad']

    # Participaciones en gol
    max_participaciones_id = df_filtrado['G+A'].idxmax()
    participaciones = df_filtrado.loc[max_participaciones_id, 'Player']
    cantidad_participaciones = df_filtrado.loc[max_participaciones_id, 'G+A']
    equipo_participaciones = df_filtrado.loc[max_participaciones_id, 'Squad']

    
    with st.container(horizontal=True, horizontal_alignment="right", border=True):
        st.metric(label=f"**Máximo anotador:** {goleador} de {equipo_goleador} con:",
                  value=f" {cantidad_goles}  goles ", icon="⚽️", border=True)
        st.metric(label=f"**Máximo asistidor:** {asistencias} de {equipo_asistencia} con",
                  value=f" {cantidad_asistencias} asistencias ", icon="👟️", border=True)
        st.metric(label=f"**Mayor participación en goles:** {participaciones} de {equipo_participaciones} con",
                  value=f" {cantidad_participaciones} participaciones", icon="🎖️", border=True)
    st.dataframe(df_filtrado,hide_index=True)

    col_4, col_5 = st.columns(2)

    with col_4:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(data=df_filtrado, x="Age", ax=ax)
        ax.set_title("Distribución por edades")
        plt.tight_layout()
        st.caption(
            f"El promedio de edad es de {round(df_filtrado.Age.mean(), 1)} años")
        st.pyplot(fig)
    with col_5:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.countplot(data=df_filtrado, x="Pos", ax=ax)
        ax.set_title("Distribución por posición")
        plt.tight_layout()
        st.pyplot(fig)

    col_6, col_7 = st.columns(2)

    with col_6:
        fig, ax = plt.subplots()
        filtro_paises = df_filtrado[df_filtrado['Nation']
                                    != "COL"]["Nation"].value_counts()
        top_paises = filtro_paises.head(4)
        otros_paises = filtro_paises.iloc[4:].sum()
        serie_otros_paises = pd.Series({"OTROS": otros_paises})
        columns = pd.concat([top_paises, serie_otros_paises])
        ax.pie(columns.values, labels=columns.index, startangle=90,
               autopct='%1.1f%%', pctdistance=1.45, counterclock=False)
        ax.set_title("Distribución por país")
        plt.tight_layout()
        st.caption(
            f"Hay {sum(map(lambda x: x != "COL", df_filtrado.Nation))} jugadores extranjeros")
        st.pyplot(fig)
    with col_7:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(data=df_filtrado, x="Min", ax=ax)
        ax.set_title("Minutos jugados")
        plt.tight_layout()
        st.pyplot(fig)
