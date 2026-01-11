#!/usr/bin/env python3
"""
Script para ver datos de la base de datos PostgreSQL
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ No se encontró DATABASE_URL en .env")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print("✅ Conectado a PostgreSQL\n")
    
    # Ver total de snapshots
    cursor.execute("SELECT COUNT(*) as count FROM market_snapshots")
    snapshots = cursor.fetchone()['count']
    print(f"📊 Total snapshots: {snapshots}")
    
    # Ver total de oportunidades
    cursor.execute("SELECT COUNT(*) as count FROM arbitrage_opportunities")
    opps = cursor.fetchone()['count']
    print(f"💰 Total oportunidades: {opps}")
    
    # Ver total de cotizaciones
    cursor.execute("SELECT COUNT(*) as count FROM exchange_quotes")
    quotes = cursor.fetchone()['count']
    print(f"💱 Total cotizaciones: {quotes}\n")
    
    if snapshots > 0:
        # Ver últimos snapshots
        print("📸 Últimos 5 snapshots:")
        cursor.execute("""
            SELECT timestamp, coin, fiat, num_exchanges
            FROM market_snapshots
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  {row['timestamp']} | {row['coin']}/{row['fiat']} | {row['num_exchanges']} exchanges")
    
    if opps > 0:
        print("\n💡 Últimas 10 oportunidades:")
        cursor.execute("""
            SELECT 
                ao.created_at,
                ms.coin,
                ms.fiat,
                ao.buy_exchange,
                ao.sell_exchange,
                ao.spread_percentage,
                ao.profit_per_unit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            ORDER BY ao.created_at DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['created_at']} | {row['coin']}/{row['fiat']}")
            print(f"    {row['buy_exchange']} → {row['sell_exchange']}")
            print(f"    Spread: {row['spread_percentage']:.2f}% | Ganancia: {row['profit_per_unit']:.2f} {row['fiat']}\n")
    
    # Ver exchanges más activos
    if opps > 0:
        print("🏆 Top 5 Exchanges (compra):")
        cursor.execute("""
            SELECT buy_exchange, COUNT(*) as count
            FROM arbitrage_opportunities
            GROUP BY buy_exchange
            ORDER BY count DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  {row['buy_exchange']}: {row['count']} veces")
        
        print("\n🏆 Top 5 Exchanges (venta):")
        cursor.execute("""
            SELECT sell_exchange, COUNT(*) as count
            FROM arbitrage_opportunities
            GROUP BY sell_exchange
            ORDER BY count DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"  {row['sell_exchange']}: {row['count']} veces")
    
    conn.close()
    
    if snapshots == 0:
        print("\n⏳ La base de datos aún está vacía")
        print("💡 Railway está guardando datos. Espera unos minutos y vuelve a ejecutar este script.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
