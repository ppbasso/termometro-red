import os
import requests
from dotenv import load_dotenv

load_dotenv()

def radiografia_predictor(paradero_id, token):
    # La URL de tu Network Tab
    url_api = "https://www.red.cl/predictorPlus/prediccion"
    
    # Parámetros y Headers exactos
    params = {"t": token, "codsimt": paradero_id, "codser": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.red.cl/planifica-tu-viaje/cuando-llega/?codsimt={paradero_id}",
        "X-Requested-With": "XMLHttpRequest"
    }

    print(f"[*] INICIANDO RADIOGRAFÍA TÁCTICA para paradero {paradero_id}...")

    try:
        # Disparo de la petición
        respuesta = requests.get(url_api, params=params, headers=headers, timeout=15)
        
        print(f"[*] Código HTTP del Gobierno: {respuesta.status_code}")
        
        # IMPRESIÓN CRUDA: Aquí veremos la verdad sin filtros ni parseos que rompan el código
        print("-" * 50)
        print("[RAW DATA INICIO]")
        print(respuesta.text)
        print("[RAW DATA FIN]")
        print("-" * 50)

    except Exception as e:
        print(f"[!] Error de conexión en la radiografía: {e}")

if __name__ == "__main__":
    # La llave maestra (Asegúrate de que siga viva, si da error de expiración, sacamos otra)
    TOKEN_MAESTRO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NzU5NzI4ODN9.krrvifhYN55uEB0KuFCCWYuz-Tpvoj8nyLDaMzQVtrE"
    radiografia_predictor("PA433", TOKEN_MAESTRO)