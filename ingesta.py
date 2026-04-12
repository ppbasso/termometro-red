import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_realidad_correcta(paradero_id):
    # Endpoint exacto que alimenta la vista de tu captura de pantalla
    url_api = f"https://www.red.cl/rest/cuando-llega/parada/{paradero_id}"
    
    # Camuflaje: Headers de navegador para evitar el bloqueo por IP
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "Connection": "keep-alive"
    }
    
    print(f"[*] Modo Stealth: Consultando paradero {paradero_id} en la ruta real...")
    
    try:
        # Petición a la API del gobierno
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Navegación del JSON: servicios -> item -> distanciaBuses
        if "servicios" in datos and "item" in datos["servicios"]:
            for servicio in datos["servicios"]["item"]:
                recorrido = servicio.get("servicio")
                
                # 'distanciaBuses' es la clave donde vienen las patentes en este endpoint
                if "distanciaBuses" in servicio:
                    for bus in servicio.get("distanciaBuses", []):
                        patente = bus.get("patente", "DESCONOCIDO").replace("-", "")
                        
                        # Limpieza y conversión de telemetría (m y min)
                        distancia = int(''.join(filter(str.isdigit, str(bus.get("distancia", "0")))))
                        minutos = int(''.join(filter(str.isdigit, str(bus.get("tiempo", "0")))))

                        if patente != "DESCONOCIDO" and distancia > 0:
                            sql = """
                                INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                            registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO! {registros} buses del paradero {paradero_id} inyectados correctamente.")
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Paradero PA433 (Escuela de Ingeniería) confirmado con data en tu captura
    inyectar_realidad_correcta("PA433")