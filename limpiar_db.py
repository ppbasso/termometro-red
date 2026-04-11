import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
url_db = os.getenv("DATABASE_URL")

print("[*] Conectando a Neon.tech para purgar la bóveda...")
try:
    conexion = psycopg2.connect(url_db)
    cursor = conexion.cursor()
    # TRUNCATE borra todo y RESTART IDENTITY reinicia los IDs a 1
    cursor.execute("TRUNCATE TABLE telemetria_buses RESTART IDENTITY;")
    conexion.commit()
    print("[+] Base de datos vaciada con éxito. Basura eliminada.")
except Exception as e:
    print(f"[!] Error: {e}")
finally:
    if 'conexion' in locals() and conexion:
        cursor.close()
        conexion.close()