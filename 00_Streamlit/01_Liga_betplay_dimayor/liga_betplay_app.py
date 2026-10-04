import pandas as pd
import streamlit as st
import requests
import io
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

with st.container(horizontal=True, horizontal_alignment="right",border=True):
    st.image("/home/daniel_cardenas/Desarrollo/Pruebas/Streamlit/Liga_betplay_dimayor/liga-betplay-dimayor.png",width=100)
    st.title("Liga BetPlay Dimayor EDA")

st.markdown("""
Esta es una aplicación de webscraping de las estadisticas historicas de la liga de futbol profesional colombiana,

• **Rk** -- Rango (Rank) Este es un conteo de las filas de arriba hacia abajo.Se recalcula después de ordenar una columna.                               
• **Nation** -- Nacionalidad del jugador. Primero, verificamos nuestros registros en partidos internacionales a nivel absoluto (selección mayor).Luego a nivel juvenil.Después, la ciudadanía presentada en Wikipedia.Finalmente, usamos su lugar de nacimiento cuando está disponible.          
• **Pos** -- Posición, Posición que el jugador desempeña con más frecuencia:                      
    • GK - Porteros                                                        
    • DF - Defensas                                                        
    • MF - Mediocampistas                                                  
    • FW - Delanteros                                                      
• **Age** -- Edad al inicio de la temporada Se calcula al 1 de agosto para las ligas de invierno y al 1 de febrero para las ligas de verano.                                                       
• **Born** -- Año de nacimiento                                                
                                                                            
### Playing Time (Tiempo de Juego)                                         
                                                                            
• **MP** -- Partidos Jugados Partidos jugados por el jugador o el equipo.                               
• **Starts** -- Titularidades Partido o partidos iniciados por el jugador como titular.                  
• **Min** -- Minutos
• **90s** -- Fracciones de 90 minutos jugados Minutos totales jugados divididos por 90.                                  
                                                                            
### Performance (Rendimiento)                                              
                                                                            
• **Gls** -- Goles, Goles marcados o permitidos.                                               
• **Ast** -- Asistencias                                                       
• **G+A** -- Goles + Asistencias                                               
• **G-PK** -- Goles sin contar penaltis (Goles de jugada)                      
• **PK** -- Tiros de penalti marcados                                          
• **PKatt** -- Tiros de penalti intentados                                     
• **CrdY** -- Tarjetas Amarillas                                               
• **CrdR** -- Tarjetas Rojas                                                   


""")

sns.set_theme(style = "whitegrid", palette="viridis")

st.sidebar.header("Filtros")
temporada_filtro = st.sidebar.selectbox('Temporada',list(reversed(range(2022,2027))))



# https://fbref.com/en/comps/41/2025/stats/2025-Primera-A-Stats

@st.cache_data
def cargar_datos(temp):
    url =f"/home/daniel_cardenas/Desarrollo/Pruebas/Streamlit/Liga_betplay_dimayor/data/{temp}.csv"
    try:
        df= pd.read_csv(url)
        df=df.dropna()
        df=df.drop(columns={'Gls.1','Ast.1','G+A.1','G-PK.1','G+A-PK','Matches','-9999'})
        df['Age'] = temp-df.Born
        df['Prom'] = round(df['Gls'] / df['MP'],2)
        df['Nation'] = df['Nation'].str[3:]
        return df
    except Exception as e:
        st.error(f"Se genero un error al cargar los datos: {e}")
        return None

df = cargar_datos(temporada_filtro)

# Filtro de equipos

equipos = sorted(df.Squad.unique())
equipo_filtro = st.sidebar.multiselect('Equipo',equipos,equipos)

#Filtro de posición

posicion = sorted(df.Pos.unique())
posicion_filtro = st.sidebar.multiselect('Posición',posicion,posicion)

df_filtrado = df[(df.Squad.isin(equipo_filtro)&(df.Pos.isin(posicion_filtro)))]

if df_filtrado.empty:
    st.warning("Por favor selecciona al menos un equipo y una posición para visualizar los datos", icon="⚠️")
else:
    #Goleador
    max_goles_id = df_filtrado['Gls'].idxmax()
    goleador = df_filtrado.loc[max_goles_id,'Player']
    cantidad_goles = df_filtrado.loc[max_goles_id,'Gls']
    equipo_goleador = df_filtrado.loc[max_goles_id,'Squad']


    #Asistencias
    max_asistencias_id = df_filtrado['Ast'].idxmax()
    asistencias = df_filtrado.loc[max_asistencias_id,'Player']
    cantidad_asistencias = df_filtrado.loc[max_asistencias_id,'Ast']
    equipo_asistencia = df_filtrado.loc[max_asistencias_id,'Squad']

    #Participaciones en gol
    max_participaciones_id = df_filtrado['G+A'].idxmax()
    participaciones = df_filtrado.loc[max_participaciones_id,'Player']
    cantidad_participaciones = df_filtrado.loc[max_participaciones_id,'G+A']
    equipo_participaciones = df_filtrado.loc[max_participaciones_id,'Squad']

    st.subheader(f"Estadisticas de la temporada {temporada_filtro} y se cargaron {len(df)} registros")

    with st.container(horizontal=True, horizontal_alignment="right",border=True):
        st.metric(label=f"**Máximo anotador:** {goleador} de {equipo_goleador} con:",value=f" {cantidad_goles}  goles ",icon="⚽️",border=True)
        st.metric(label=f"**Máximo asistidor:** {asistencias} de {equipo_asistencia} con",value=f" {cantidad_asistencias} asistencias ",icon="👟️",border=True)
        st.metric(label=f"**Mayor participación en goles:** {participaciones} de {equipo_participaciones} con",value=f" {cantidad_participaciones} participaciones",icon="🎖️",border=True )
    st.dataframe(df_filtrado)

    col_4, col_5 = st.columns(2)

    with col_4:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(data= df_filtrado, x="Age", ax=ax)
        ax.set_title("Distribución por edades")
        plt.tight_layout()
        st.caption(f"El promedio de edad es de {round(df_filtrado.Age.mean(),1)} años")
        st.pyplot(fig)
    with col_5:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.countplot(data= df_filtrado, x="Pos",ax=ax)
        ax.set_title("Distribución por posición")
        plt.tight_layout()
        st.pyplot(fig)

    col_6, col_7=st.columns(2)

    with col_6:
        fig, ax = plt.subplots()
        filtro_paises= df_filtrado[df_filtrado['Nation']!="COL"]["Nation"].value_counts()
        top_paises = filtro_paises.head(4)
        otros_paises = filtro_paises.iloc[4:].sum()
        serie_otros_paises = pd.Series({"OTROS": otros_paises})
        columns = pd.concat([top_paises,serie_otros_paises])
        ax.pie(columns.values, labels=columns.index,startangle=90,autopct='%1.1f%%',pctdistance=1.45,counterclock=False)
        ax.set_title("Distribución por país")
        plt.tight_layout()
        st.caption(f"Hay {sum(map(lambda x: x != "COL",df_filtrado.Nation))} jugadores extranjeros")
        st.pyplot(fig)
    with col_7:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(data= df_filtrado, x="Min",ax=ax)
        ax.set_title("Minutos jugados")
        plt.tight_layout()
        st.pyplot(fig)






    



