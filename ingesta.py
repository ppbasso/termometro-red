import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_predictor_plus(paradero_id, token):
    # La URL real descubierta en el Network Tab (PredictorPlus)
    url_api = "https://www.red.cl/predictorPlus/prediccion"
    
    # Parámetros exactos extraídos de tu captura
    params = {
        "t": token,
        "codsimt": paradero_id,
        "codser": ""
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"[*] Accediendo vía PredictorPlus con Token JWT para paradero {paradero_id}...")

    try:
        respuesta = requests.get(url_api, params=params, headers=headers, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión con PredictorPlus: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # PredictorPlus suele agrupar por servicios directamente
        servicios = datos.get("servicios", [])
        for servicio in servicios:
            recorrido = servicio.get("servicio")
            # En este endpoint los buses suelen venir en la lista 'buses'
            buses = servicio.get("buses", [])
            for bus in buses:
                patente = bus.get("patente", "").replace("-", "")
                
                # Conversión segura de strings a números
                try:
                    distancia = int(''.join(filter(str.isdigit, str(bus.get("distancia", "0")))))
                    minutos = int(''.join(filter(str.isdigit, str(bus.get("tiempo", "0")))))
                except ValueError:
                    continue

                if patente:
                    sql = """
                        INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                    registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO! {registros} buses inyectados usando la llave PredictorPlus.")
        
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Token JWT extraído de tu mensaje
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    inyectar_predictor_plus("PA433", TOKEN_MAESTRO)