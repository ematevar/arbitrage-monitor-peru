#!/usr/bin/env python3
"""
Script rápido para verificar conexión a PostgreSQL de Railway
"""
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL en .env")
    print("\n📝 Pasos:")
    print("1. En Railway, click en PostgreSQL")
    print("2. Pestaña 'Connect' o 'Variables'")
    print("3. Copiar 'Postgres Connection URL'")
    print("4. Crear archivo .env con:")
    print("   DATABASE_URL=postgresql://...")
    exit(1)

try:
    import psycopg2
    print("✓ psycopg2 instalado")
    
    print(f"\n🔌 Conectando a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ ¡Conexión exitosa!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"📊 PostgreSQL version: {version[0]}")
    
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()
    print(f"💾 Base de datos: {db_name[0]}")
    
    conn.close()
    print("\n🎉 PostgreSQL está funcionando correctamente")
    
except ImportError:
    print("❌ psycopg2 no instalado")
    print("Instalar con: pip install psycopg2-binary")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Posibles causas:")
    print("- PostgreSQL aún se está inicializando (espera 1-2 min)")
    print("- DATABASE_URL incorrecta")
    print("- Firewall bloqueando conexión")
