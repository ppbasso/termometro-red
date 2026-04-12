import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_realidad_publica(paradero_id):
    # Endpoint CORRECTO de la web pública de Red (Singular: parada)
    url_api = f"https://www.red.cl/rest/parada/{paradero_id}"
    
    # Camuflaje: Spoofing de User-Agent (Mantenemos lo que ya funcionó)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.red.cl/",
        "Connection": "keep-alive"
    }
    
    print(f"[*] Modo Stealth: Consultando parada {paradero_id}...")
    
    try:
        # Petición con el endpoint corregido
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    if not url_db:
        print("[!] ERROR: Variable DATABASE_URL no encontrada.")
        return

    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # El JSON de red.cl agrupa por 'servicios' -> 'item'
        if "servicios" in datos and "item" in datos["servicios"]:
            for servicio in datos["servicios"]["item"]:
                recorrido = servicio.get("servicio")
                
                # 'distanciaBuses' contiene la telemetría real de cada bus en camino
                if "distanciaBuses" in servicio:
                    for bus in servicio.get("distanciaBuses", []):
                        # Limpieza: Quitamos guiones de la patente
                        patente = bus.get("patente", "DESCONOCIDO").replace("-", "")
                        
                        # Conversión: Extraemos solo los números de "450 metros" o "02 min."
                        try:
                            distancia_str = str(bus.get("distancia", "0"))
                            distancia = int(''.join(filter(str.isdigit, distancia_str)))
                        except ValueError:
                            distancia = 0
                            
                        try:
                            tiempo_str = str(bus.get("tiempo", "0"))
                            minutos = int(''.join(filter(str.isdigit, tiempo_str)))
                        except ValueError:
                            minutos = 0

                        if patente != "DESCONOCIDO":
                            sql = """
                                INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                            registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO! {registros} buses inyectados a Neon desde la parada {paradero_id}.")
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Probamos con el paradero que estabas usando
    inyectar_realidad_publica("PA433")