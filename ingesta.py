import json
import os
import psycopg2
from dotenv import load_dotenv

# Carga las variables secretas desde el archivo .env a la memoria
load_dotenv()

def inyectar_telemetria():
    """
    Lee el archivo JSON local simulado y guarda los registros en la base de datos PostgreSQL.
    """
    ruta_archivo = "dummy_pa433.json"
    
    # 1. Leer los datos locales
    if not os.path.exists(ruta_archivo):
        print(f"[!] Error: El archivo {ruta_archivo} no existe.")
        return

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
    
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