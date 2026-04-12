import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def inyectar_realidad_publica(paradero_id):
    # Endpoint de la web pública de Red (Puerta trasera ciudadana)
    url_api = f"https://www.red.cl/rest/paraderos/{paradero_id}"
    
    # Camuflaje: Spoofing de User-Agent simulando Chrome en Windows 11
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.red.cl/",
        "Connection": "keep-alive"
    }
    
    print(f"[*] Modo Stealth: Consultando web pública para paradero {paradero_id}")
    
    try:
        # Ejecutamos la petición con el camuflaje puesto
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error de conexión con servidor público: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    if not url_db:
        print("[!] ERROR: Variable DATABASE_URL no encontrada en el entorno.")
        return

    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Parseo del árbol JSON del gobierno
        if "servicios" in datos and "item" in datos["servicios"]:
            for servicio in datos["servicios"]["item"]:
                recorrido = servicio.get("servicio")
                
                # Validamos si el servicio tiene buses en ruta informados
                if "distanciaBuses" in servicio:
                    for bus in servicio.get("distanciaBuses", []):
                        # Limpieza de caracteres basura ("ABCD-12" -> "ABCD12")
                        patente = bus.get("patente", "DESCONOCIDO").replace("-", "")
                        
                        # Conversión de texto a número entero ("400 metros" -> 400)
                        try:
                            distancia = int(''.join(filter(str.isdigit, str(bus.get("distancia", "0")))))
                        except ValueError:
                            distancia = 0
                            
                        # Conversión de tiempo a entero ("02 min." -> 2)
                        try:
                            minutos = int(''.join(filter(str.isdigit, str(bus.get("tiempo", "0")))))
                        except ValueError:
                            minutos = 0

                        if patente != "DESCONOCIDO" and distancia > 0:
                            sql = """
                                INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (paradero_id, recorrido, patente, distancia, minutos))
                            registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO! {registros} registros inyectados desde infraestructura web gubernamental.")
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    inyectar_realidad_publica("PA433")