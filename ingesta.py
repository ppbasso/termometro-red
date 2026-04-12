import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_realidad_final(paradero_id):
    # Endpoint SINGULAR (itinerario): La llave maestra definitiva
    url_api = f"https://www.red.cl/rest/v1/itinerario/parada/{paradero_id}"
    
    # Headers extraídos de una sesión real de navegación en red.cl
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    print(f"[*] Modo Stealth Final: Consultando {url_api}")
    
    try:
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        # Si esto da 404, el servidor cambió la estructura en el último minuto
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión en la ruta final: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Procesamiento del JSON oficial
        if "servicios" in datos and "item" in datos["servicios"]:
            for servicio in datos["servicios"]["item"]:
                recorrido = servicio.get("servicio")
                
                if "distanciaBuses" in servicio:
                    for bus in servicio.get("distanciaBuses", []):
                        patente = bus.get("patente", "N/A").replace("-", "")
                        
                        # Conversión de telemetría: "1.2 km" -> 1200 o "05 min." -> 5
                        try:
                            # Limpieza profunda de strings a números
                            dist_str = str(bus.get("distancia", "0"))
                            distancia = int(''.join(filter(str.isdigit, dist_str)))
                            
                            tiempo_str = str(bus.get("tiempo", "0"))
                            minutos = int(''.join(filter(str.isdigit, tiempo_str)))
                        except ValueError:
                            continue

                        if patente and patente != "N/A":
                            sql = """
                                INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                            registros += 1
        
        conexion.commit()
        print(f"[+] ¡MISIÓN CUMPLIDA! {registros} buses inyectados para {paradero_id}.")
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # PA433: El paradero que confirmamos con data en tu navegador
    inyectar_realidad_final("PA433")