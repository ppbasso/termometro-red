import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_realidad_transapp(paradero_id):
    # API de Transapp: El estándar de facto de la comunidad cuando el DTPM falla
    url_api = f"https://api.transapp.cl/v1/prediction/stop/{paradero_id}"
    
    print(f"[*] Consultando Transapp (SLA Estable): {paradero_id}")
    try:
        # Transapp es rápido, 10s de timeout es más que suficiente
        respuesta = requests.get(url_api, timeout=60)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión con Transapp: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Transapp devuelve una lista de predicciones directa
        for prediccion in datos.get("predictions", []):
            recorrido = prediccion.get("route_id")
            for bus in prediccion.get("buses", []):
                patente = bus.get("bus_id")
                distancia = bus.get("distance_meters")
                minutos = bus.get("arrival_minutes")

                if patente and distancia is not None:
                    sql = """
                        INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                    registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO! {registros} registros inyectados desde infraestructura de Transapp.")
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    inyectar_realidad_transapp("PA433")