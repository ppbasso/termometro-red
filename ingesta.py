import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def inyectar_predictor_oficial(paradero_id, token):
    # 1. URL del Gobierno
    url_api_gob = "https://www.red.cl/predictorPlus/prediccion"
    params = {"t": token, "codsimt": paradero_id, "codser": ""}
    
    headers_gob = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"[*] Modo Producción: Extrayendo PredictorPlus para {paradero_id}...")

    try:
        respuesta = requests.get(url_api_gob, params=params, headers=headers_gob, timeout=15)
        respuesta.raise_for_status()
        
        try:
            datos = respuesta.json()
        except json.JSONDecodeError:
            print(f"[!] Error crítico: El servidor del gobierno no devolvió JSON válido. (Token expirado)")
            return
            
    except Exception as e:
        print(f"[!] Error de conexión con el gobierno: {e}")
        return

    # 2. URL de TU Controlador en la capa de Backend (Hugging Face)
    url_tu_api = "https://ppbasso-termometro-red-api.hf.space/api/telemetria"
    registros = 0

    if "servicios" in datos and "item" in datos["servicios"]:
        for servicio in datos["servicios"]["item"]:
            recorrido = servicio.get("servicio", "N/A")
            
            # --- Procesamiento Bus 1 ---
            patente_1 = servicio.get("ppubus1", "").replace("-", "")
            distancia_1_str = servicio.get("distanciabus1", "")
            minutos_1_str = servicio.get("horaprediccionbus1", "")
            
            if patente_1 and patente_1 != "":
                try:
                    distancia_1 = int(''.join(filter(str.isdigit, str(distancia_1_str)))) if distancia_1_str else 0
                    numeros_tiempo = [int(s) for s in str(minutos_1_str).split() if s.isdigit()]
                    minutos_1 = numeros_tiempo[0] if numeros_tiempo else 0

                    payload = {
                        "paradero": paradero_id,
                        "recorrido": recorrido,
                        "patente": patente_1,
                        "distanciaMetros": distancia_1,
                        "tiempoEstimadoMin": minutos_1
                    }
                    
                    resp = requests.post(url_tu_api, json=payload, timeout=10)
                    if resp.status_code in [200, 201]:
                        registros += 1
                    else:
                        print(f"[!] Tu API rechazó el Bus 1 (HTTP {resp.status_code}): {resp.text}")
                except Exception as err:
                    print(f"[!] Error enviando Bus 1: {err}")

            # --- Procesamiento Bus 2 ---
            patente_2 = servicio.get("ppubus2", "").replace("-", "")
            distancia_2_str = servicio.get("distanciabus2", "")
            minutos_2_str = servicio.get("horaprediccionbus2", "")
            
            if patente_2 and patente_2 != "":
                try:
                    distancia_2 = int(''.join(filter(str.isdigit, str(distancia_2_str)))) if distancia_2_str else 0
                    numeros_tiempo_2 = [int(s) for s in str(minutos_2_str).split() if s.isdigit()]
                    minutos_2 = numeros_tiempo_2[0] if numeros_tiempo_2 else 0

                    payload = {
                        "paradero": paradero_id,
                        "recorrido": recorrido,
                        "patente": patente_2,
                        "distanciaMetros": distancia_2,
                        "tiempoEstimadoMin": minutos_2
                    }
                    
                    resp = requests.post(url_tu_api, json=payload, timeout=10)
                    if resp.status_code in [200, 201]:
                        registros += 1
                    else:
                        print(f"[!] Tu API rechazó el Bus 2 (HTTP {resp.status_code}): {resp.text}")
                except Exception as err:
                    print(f"[!] Error enviando Bus 2: {err}")

    # Lógica de mensajes corregida
    if registros > 0:
        print(f"[+] ¡ÉXITO TOTAL! {registros} buses procesados a través de tu Controlador Java.")
    else:
        print(f"[!] MISIÓN FALLIDA: 0 buses insertados. Revisa el @PostMapping de tu API Java.")

if __name__ == "__main__":
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    inyectar_predictor_oficial("PA433", TOKEN_MAESTRO)