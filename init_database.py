#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Railway
Crea la base de datos y las tablas necesarias
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL")
    exit(1)

print("🔧 Inicializando base de datos en Railway...")

# Conectar al servidor PostgreSQL (sin especificar base de datos)
try:
    # Extraer componentes de la URL
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if not match:
        print("❌ DATABASE_URL inválida")
        exit(1)
    
    user, password, host, port, dbname = match.groups()
    
    # Conectar al servidor (base de datos 'postgres' por defecto)
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database='postgres'  # Conectar a la BD por defecto
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Verificar si la base de datos existe
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f"✓ Base de datos '{dbname}' ya existe")
    else:
        print(f"📝 Creando base de datos '{dbname}'...")
        cursor.execute(f'CREATE DATABASE "{dbname}"')
        print(f"✅ Base de datos '{dbname}' creada exitosamente")
    
    cursor.close()
    conn.close()
    
    # Ahora conectar a la base de datos específica y crear tablas
    print(f"\n🔧 Creando tablas en '{dbname}'...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Crear tablas del esquema avanzado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            coin VARCHAR(20) NOT NULL,
            fiat VARCHAR(10) NOT NULL,
            volume DECIMAL(20, 8) NOT NULL,
            snapshot_hash VARCHAR(64) UNIQUE,
            num_exchanges INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_quotes (
            id SERIAL PRIMARY KEY,
            snapshot_id INTEGER REFERENCES market_snapshots(id) ON DELETE CASCADE,
            exchange VARCHAR(100) NOT NULL,
            ask DECIMAL(20, 8),
            bid DECIMAL(20, 8),
            total_ask DECIMAL(20, 8),
            total_bid DECIMAL(20, 8),
            api_timestamp BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
            id SERIAL PRIMARY KEY,
            snapshot_id INTEGER REFERENCES market_snapshots(id) ON DELETE CASCADE,
            buy_exchange VARCHAR(100) NOT NULL,
            sell_exchange VARCHAR(100) NOT NULL,
            buy_price DECIMAL(20, 8) NOT NULL,
            sell_price DECIMAL(20, 8) NOT NULL,
            spread_percentage DECIMAL(10, 4) NOT NULL,
            profit_per_unit DECIMAL(20, 8) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON market_snapshots(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_coin_fiat ON market_snapshots(coin, fiat)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_snapshot ON exchange_quotes(snapshot_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_exchange ON exchange_quotes(exchange)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_snapshot ON arbitrage_opportunities(snapshot_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_exchanges ON arbitrage_opportunities(buy_exchange, sell_exchange)")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Tablas creadas exitosamente")
    print("\n🎉 Base de datos inicializada correctamente")
    print("\n💡 Ahora puedes:")
    print("   1. Hacer redeploy en Railway")
    print("   2. El monitor se conectará automáticamente a PostgreSQL")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
