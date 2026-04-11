import json
import os
import psycopg2
import requests
from dotenv import load_dotenv

# Carga las variables secretas desde el archivo .env a la memoria
load_dotenv()

def inyectar_telemetria():
    """
    Consulta la API en vivo de RED y guarda los registros en la base de datos PostgreSQL.
    """
    url_api = "https://api.xor.cl/red/bus-stop/PA433"
    
    # 1. Obtener los datos reales de la API
    print(f"[*] Consultando API RED: {url_api}")
    try:
        # Aumentamos el timeout a 30 evita que el script se caiga por latencia de la API pública
        respuesta = requests.get(url_api, timeout=30)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error de red al consultar la API: {e}")
        return
    
    # Extraemos el ID del paradero
    id_paradero = datos.get("id", "Desconocido")
    
    # 2. Conectar a la Base de Datos
    url_db = os.getenv("DATABASE_URL")
    if not url_db:
        print("[!] Error: No se encontró la variable DATABASE_URL en el archivo .env")
        return

    print("[*] Conectando a la bóveda en Neon.tech...")
    
    try:
        # Iniciamos la conexión con el motor de Postgres
        conexion = psycopg2.connect(url_db)
        cursor = conexion.cursor()
        
        registros_insertados = 0
        
        # 3. Extraer e Insertar cada bus
        for servicio in datos.get("services", []):
            recorrido = servicio.get("id")
            
            for bus in servicio.get("buses", []):
                patente = bus.get("id")
                distancia = bus.get("meters_distance")
                minutos = bus.get("min_arrival_time")
                
                # Filtro de validación: Ignorar registros "fantasmas" que no traen telemetría útil
                if patente and distancia is not None and minutos is not None:
                    # Sentencia SQL parametrizada (%s) (La mejor práctica para evitar inyecciones SQL)
                    sql = """
                        INSERT INTO telemetria_buses (paradero, recorrido, patente, distancia_metros, tiempo_estimado_min)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    valores = (id_paradero, recorrido, patente, distancia, minutos)
                    
                    # Ejecutamos la orden
                    cursor.execute(sql, valores)
                    registros_insertados += 1
        
        # Confirmar y guardar los cambios (Commit)
        conexion.commit()
        print(f"[*] ¡Éxito! Se inyectaron {registros_insertados} registros en la base de datos histórica.")
        
    except Exception as e:
        print(f"[!] Error crítico de base de datos: {e}")
    finally:
        # Siempre cerrar la conexión, pase lo que pase, para no agotar las conexiones gratuitas de Neon
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()
            print("[*] Conexión cerrada de forma segura.")

if __name__ == "__main__":
    print("Iniciando Termómetro RED - Pipeline de Ingesta a BBDD\n" + "-"*55)
    inyectar_telemetria()