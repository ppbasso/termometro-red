import os
import psycopg2
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def inyectar_predictor_final(paradero_id, token):
    url_api = "https://www.red.cl/predictorPlus/prediccion"
    params = {"t": token, "codsimt": paradero_id, "codser": ""}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"[*] Consultando PredictorPlus para {paradero_id}...")

    try:
        respuesta = requests.get(url_api, params=params, headers=headers, timeout=15)
        respuesta.raise_for_status()
        
        # Intentamos obtener el JSON
        try:
            datos = respuesta.json()
        except:
            # Si no es JSON, capturamos el texto crudo para el log
            datos = respuesta.text

        # VALIDACIÓN DE TIPO (Aquí estaba el fallo)
        if isinstance(datos, str):
            print(f"[!] El servidor no mandó JSON. Respuesta del gobierno: {datos}")
            return

    except Exception as e:
        print(f"[!] Error de conexión: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Procesamiento robusto del diccionario
        servicios = datos.get("servicios", [])
        for servicio in servicios:
            recorrido = servicio.get("servicio")
            for bus in servicio.get("buses", []):
                patente = bus.get("patente", "").replace("-", "")
                
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
        print(f"[+] ¡ÉXITO! {registros} buses inyectados en Neon.")
        
    except Exception as e:
        print(f"[!] Error en procesamiento/DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Token JWT que sacaste del navegador (Ojo: puede durar pocos minutos)
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    inyectar_predictor_final("PA433", TOKEN_MAESTRO)