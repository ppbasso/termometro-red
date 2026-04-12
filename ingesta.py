import os
import psycopg2
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def inyectar_predictor_oficial(paradero_id, token):
    url_api = "https://www.red.cl/predictorPlus/prediccion"
    params = {"t": token, "codsimt": paradero_id, "codser": ""}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"[*] Modo Producción: Consultando PredictorPlus para {paradero_id}...")

    try:
        respuesta = requests.get(url_api, params=params, headers=headers, timeout=15)
        respuesta.raise_for_status()
        
        try:
            datos = respuesta.json()
        except json.JSONDecodeError:
            print(f"[!] Error crítico: El servidor no devolvió JSON válido. (Token expirado o WAF bloqueando)")
            return
            
    except Exception as e:
        print(f"[!] Error de conexión: {e}")
        return

    url_db = os.getenv("DATABASE_URL")
    try:
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        registros = 0

        # Navegación exacta basada en la radiografía
        if "servicios" in datos and "item" in datos["servicios"]:
            for servicio in datos["servicios"]["item"]:
                recorrido = servicio.get("servicio", "N/A")
                
                # Extracción del Bus 1
                patente_1 = servicio.get("ppubus1", "").replace("-", "")
                distancia_1_str = servicio.get("distanciabus1", "")
                minutos_1_str = servicio.get("horaprediccionbus1", "")
                
                # Solo procesamos si hay una patente válida
                if patente_1 and patente_1 != "":
                    try:
                        # Extraer solo números de la distancia (ej. "4539" -> 4539)
                        distancia_1 = int(''.join(filter(str.isdigit, distancia_1_str))) if distancia_1_str else 0
                        
                        # Extraer minutos (ej. "Entre 16 Y 20 min" -> promediamos o tomamos el menor, tomaremos 16)
                        numeros_tiempo = [int(s) for s in minutos_1_str.split() if s.isdigit()]
                        minutos_1 = numeros_tiempo[0] if numeros_tiempo else 0

                        sql = """
                            INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (paradero_id, recorrido, patente_1, distancia_1, minutos_1))
                        registros += 1

                # Extracción del Bus 2 (El JSON oficial soporta hasta 2 buses por recorrido)
                patente_2 = servicio.get("ppubus2", "").replace("-", "")
                distancia_2_str = servicio.get("distanciabus2", "")
                minutos_2_str = servicio.get("horaprediccionbus2", "")
                
                if patente_2 and patente_2 != "":
                    try:
                        distancia_2 = int(''.join(filter(str.isdigit, distancia_2_str))) if distancia_2_str else 0
                        numeros_tiempo_2 = [int(s) for s in minutos_2_str.split() if s.isdigit()]
                        minutos_2 = numeros_tiempo_2[0] if numeros_tiempo_2 else 0

                        sql = """
                            INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (paradero_id, recorrido, patente_2, distancia_2, minutos_2))
                        registros += 1
        
        conexion.commit()
        print(f"[+] ¡ÉXITO TOTAL! {registros} buses reales inyectados en la base de datos Neon.")
        
    except Exception as e:
        print(f"[!] Error DB: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Token JWT
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    inyectar_predictor_oficial("PA433", TOKEN_MAESTRO)