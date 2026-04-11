import streamlit as st
import requests
import pandas as pd

# 1. Configuración de la página (Filosofía Mobile-First)
st.set_page_config(page_title="Termómetro RED", page_icon="🚌", layout="centered")

# UI/UX: Encabezado ciudadano
st.title("🚌 La Realidad del Paradero")
st.markdown("Auditor Ciudadano del Transantiago. Datos en vivo, sin falacias.")
st.divider()

# 2. Buscador Interactivo
st.subheader("¿Qué micro tomas?")
# Limpieza del input: quita espacios y pasa a mayúsculas automáticamente
recorrido_input = st.text_input("Ingresa tu recorrido", placeholder="Ej. 210, 506, I09").strip().upper()

if recorrido_input:
    # 3. Conexión dinámica a la API Java
    API_URL = f"http://localhost:8080/api/telemetria?recorrido={recorrido_input}"
    
    try:
        with st.spinner(f'Auditando la realidad del recorrido {recorrido_input}...'):
            respuesta = requests.get(API_URL)
            
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            if datos:
                df = pd.DataFrame(datos)
                
                # --- Motor Lógico Frontend ---
                # Contamos buses únicos (patentes) para no duplicar si el backend envía históricos repetidos
                total_buses = df['patente'].nunique()
                
                # Criterio: Si la distancia es > 50m, está en movimiento. Si es menor, está en terminal/paradero.
                buses_en_movimiento = df[df['distanciaMetros'] > 50]['patente'].nunique()
                buses_detenidos = total_buses - buses_en_movimiento
                
                # Frecuencia estimada (promedio de los 3 buses más cercanos)
                df_ordenado = df.sort_values(by='tiempoEstimadoMin')
                frecuencia_real = df_ordenado['tiempoEstimadoMin'].head(3).mean()
                if pd.isna(frecuencia_real):
                    frecuencia_real = 0

                # 4. Renderizado de Tarjetas de Verdad
                st.markdown("### El Veredicto:")
                
                st.info(f"**Salud del Recorrido Ahora:** Detectamos **{total_buses}** buses de la ruta {recorrido_input}. Hay **{buses_en_movimiento}** circulando y **{buses_detenidos}** detenidos/estacionados.")
                
                st.warning("**Comparativa Histórica:** [Módulo Forense en construcción] Requiere acumular más días de datos en PostgreSQL.")
                
                st.success(f"**Frecuencia Real Estimada:** Los próximos buses promedian una llegada cada **{int(frecuencia_real)}** minutos.")
                
                with st.expander("🕵️‍♂️ Ver telemetría cruda del sistema"):
                    df_limpio = df[['patente', 'paradero', 'distanciaMetros', 'tiempoEstimadoMin']].drop_duplicates()
                    df_limpio.columns = ['Patente', 'Paradero ID', 'Distancia (m)', 'Tiempo (min)']
                    st.dataframe(df_limpio, width='stretch', hide_index=True)
                    
            else:
                st.warning(f"La API no devolvió datos para el recorrido **{recorrido_input}**.")
        else:
            st.error(f"Error del servidor backend. Código HTTP: {respuesta.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("🚨 CRÍTICO: No se pudo conectar a la API. ¿Está el servidor Java encendido en la otra terminal?")
else:
    st.caption("Escribe el nombre de tu recorrido y presiona Enter para auditar.")