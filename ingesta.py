import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def inyectar_predictor_oficial(paradero_id, token):
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
            print(f"[!] Error crítico: Token expirado. Actualiza el token en el código.")
            return
    except Exception as e:
        print(f"[!] Error de conexión con el gobierno: {e}")
        return

    url_tu_api = "https://ppbasso-termometro-red-api.hf.space/api/telemetria"
    registros = 0

    # Procesamiento 100% de buses reales
    if "servicios" in datos and "item" in datos["servicios"]:
        for servicio in datos["servicios"]["item"]:
            recorrido = servicio.get("servicio", "N/A")
            
            # Bus 1
            patente_1 = servicio.get("ppubus1", "").replace("-", "")
            if patente_1 and patente_1 != "":
                distancia_1_str = servicio.get("distanciabus1", "")
                minutos_1_str = servicio.get("horaprediccionbus1", "")
                distancia_1 = int(''.join(filter(str.isdigit, str(distancia_1_str)))) if distancia_1_str else 0
                numeros_tiempo = [int(s) for s in str(minutos_1_str).split() if s.isdigit()]
                minutos_1 = numeros_tiempo[0] if numeros_tiempo else 0

                payload = {"paradero": paradero_id, "recorrido": recorrido, "patente": patente_1, "distanciaMetros": distancia_1, "tiempoEstimadoMin": minutos_1}
                try:
                    resp = requests.post(url_tu_api, json=payload, timeout=10)
                    if resp.status_code in [200, 201]: registros += 1
                    else: print(f"[!] Tu API rechazó el Bus 1 (HTTP {resp.status_code}): {resp.text}")
                except Exception as err: print(f"[!] Error enviando Bus 1 a Java: {err}")

            # Bus 2
            patente_2 = servicio.get("ppubus2", "").replace("-", "")
            if patente_2 and patente_2 != "":
                distancia_2_str = servicio.get("distanciabus2", "")
                minutos_2_str = servicio.get("horaprediccionbus2", "")
                distancia_2 = int(''.join(filter(str.isdigit, str(distancia_2_str)))) if distancia_2_str else 0
                numeros_tiempo_2 = [int(s) for s in str(minutos_2_str).split() if s.isdigit()]
                minutos_2 = numeros_tiempo_2[0] if numeros_tiempo_2 else 0

                payload = {"paradero": paradero_id, "recorrido": recorrido, "patente": patente_2, "distanciaMetros": distancia_2, "tiempoEstimadoMin": minutos_2}
                try:
                    resp = requests.post(url_tu_api, json=payload, timeout=10)
                    if resp.status_code in [200, 201]: registros += 1
                    else: print(f"[!] Tu API rechazó el Bus 2 (HTTP {resp.status_code}): {resp.text}")
                except Exception as err: print(f"[!] Error enviando Bus 2 a Java: {err}")

    if registros > 0:
        print(f"[+] ¡ÉXITO! {registros} buses REALES guardados en tu base de datos a través de Spring Boot.")
    else:
        print(f"[-] No hay buses reales en circulación a esta hora para el paradero {paradero_id}.")

if __name__ == "__main__":
    # Token JWT
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    # APUNTANDO AL PARADERO ACTIVO
    inyectar_predictor_oficial("PE155", TOKEN_MAESTRO)