import streamlit as st
import requests
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Termómetro RED", page_icon="🚌", layout="wide")
st.title("🚌 Termómetro RED - Monitor de Telemetría")
st.markdown("Dashboard en tiempo real consumiendo API REST Java Spring Boot 2.7")
st.divider()

# 2. Conexión a tu API Java
API_URL = "http://localhost:8080/api/telemetria"

try:
    with st.spinner('Consultando al servidor Java...'):
        respuesta = requests.get(API_URL)
        
    if respuesta.status_code == 200:
        datos = respuesta.json()
        
        if datos:
            # 3. Transformar el JSON feo en una tabla profesional (DataFrame)
            df = pd.DataFrame(datos)
            
            # Reordenar y renombrar columnas para que se vea nivel corporativo
            df = df[['id', 'paradero', 'recorrido', 'patente', 'distanciaMetros', 'tiempoEstimadoMin']]
            df.columns = ['ID', 'Paradero', 'Recorrido', 'Patente', 'Distancia (Metros)', 'Tiempo Estimado (Min)']
            
            # 4. Dibujar la tabla y métricas
            st.success(f"¡Conexión exitosa! {len(datos)} registros obtenidos.")
            
            col1, col2 = st.columns(2)
            col1.metric("Buses en Monitor", len(df))
            col2.metric("Menor Tiempo de Llegada (Min)", df['Tiempo Estimado (Min)'].min())
            
            st.dataframe(df, width='stretch', hide_index=True)
            
        else:
            st.info("La API respondió correctamente, pero no hay datos en la base de datos de Neon.")
    else:
        st.error(f"Error del servidor. Código HTTP: {respuesta.status_code}")

except requests.exceptions.ConnectionError:
    st.error("🚨 CRÍTICO: No se pudo conectar a la API. ¿Está el motor de Java Spring Boot encendido en el puerto 8080?")