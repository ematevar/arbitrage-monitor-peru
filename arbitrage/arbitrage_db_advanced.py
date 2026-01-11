#!/usr/bin/env python3
"""
Módulo de Base de Datos AVANZADO para Arbitraje
Esquema detallado optimizado para análisis profesional
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_batch
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

@dataclass
class MarketSnapshot:
    """Snapshot completo del mercado en un momento dado"""
    id: Optional[int]
    timestamp: datetime
    coin: str
    fiat: str
    volume: float
    snapshot_hash: str
    num_exchanges: int

@dataclass
class ExchangeQuote:
    """Cotización de un exchange específico"""
    id: Optional[int]
    snapshot_id: int
    exchange: str
    ask: Optional[float]  # Precio sin comisiones
    bid: Optional[float]  # Precio sin comisiones
    total_ask: Optional[float]  # Precio CON comisiones
    total_bid: Optional[float]  # Precio CON comisiones
    api_timestamp: Optional[int]

class ArbitrageDatabaseAdvanced:
    """Base de datos avanzada para análisis profesional de arbitraje"""
    
    def __init__(self, db_url: Optional[str] = None, db_path: str = "arbitrage_advanced.db"):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.db_path = db_path
        self.conn = None
        self.is_postgres = False
        
        if self.db_url and POSTGRES_AVAILABLE:
            self._init_postgres()
        else:
            self._init_sqlite()
    
    def _init_postgres(self):
        """Inicializa PostgreSQL"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.is_postgres = True
            self._create_postgres_tables()
            print(f"✓ Conectado a PostgreSQL (Esquema Avanzado)")
        except Exception as e:
            print(f"⚠️  Error conectando a PostgreSQL: {e}")
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Inicializa SQLite"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.is_postgres = False
        self._create_sqlite_tables()
        print(f"✓ Usando SQLite (Esquema Avanzado)")
    
    def _create_postgres_tables(self):
        """Crea tablas en PostgreSQL"""
        cursor = self.conn.cursor()
        
        # Tabla 1: Market Snapshots
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
        
        # Tabla 2: Exchange Quotes
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
        
        # Tabla 3: Arbitrage Opportunities
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
        
        # Índices optimizados
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON market_snapshots(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_coin_fiat ON market_snapshots(coin, fiat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_snapshot ON exchange_quotes(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_exchange ON exchange_quotes(exchange)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_snapshot ON arbitrage_opportunities(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_exchanges ON arbitrage_opportunities(buy_exchange, sell_exchange)")
        
        self.conn.commit()
    
    def _create_sqlite_tables(self):
        """Crea tablas en SQLite"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                coin TEXT NOT NULL,
                fiat TEXT NOT NULL,
                volume REAL NOT NULL,
                snapshot_hash TEXT UNIQUE,
                num_exchanges INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exchange_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER REFERENCES market_snapshots(id) ON DELETE CASCADE,
                exchange TEXT NOT NULL,
                ask REAL,
                bid REAL,
                total_ask REAL,
                total_bid REAL,
                api_timestamp INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER REFERENCES market_snapshots(id) ON DELETE CASCADE,
                buy_exchange TEXT NOT NULL,
                sell_exchange TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                spread_percentage REAL NOT NULL,
                profit_per_unit REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON market_snapshots(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_coin_fiat ON market_snapshots(coin, fiat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_snapshot ON exchange_quotes(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_exchange ON exchange_quotes(exchange)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_snapshot ON arbitrage_opportunities(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_exchanges ON arbitrage_opportunities(buy_exchange, sell_exchange)")
        
        self.conn.commit()
    
    def save_market_snapshot(self, coin: str, fiat: str, volume: float, quotes_data: Dict, opportunities: List) -> int:
        """
        Guarda un snapshot completo del mercado
        
        Args:
            coin: Criptomoneda
            fiat: Moneda fiat
            volume: Volumen consultado
            quotes_data: Dict con cotizaciones de todos los exchanges
            opportunities: Lista de oportunidades detectadas
            
        Returns:
            ID del snapshot creado
        """
        timestamp = datetime.now()
        
        # Crear hash único del snapshot
        snapshot_str = f"{timestamp.isoformat()}_{coin}_{fiat}_{json.dumps(quotes_data, sort_keys=True)}"
        snapshot_hash = hashlib.sha256(snapshot_str.encode()).hexdigest()
        
        cursor = self.conn.cursor()
        param = '%s' if self.is_postgres else '?'
        
        # Guardar snapshot
        if self.is_postgres:
            cursor.execute(f"""
                INSERT INTO market_snapshots (timestamp, coin, fiat, volume, snapshot_hash, num_exchanges)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (timestamp, coin, fiat, volume, snapshot_hash, len(quotes_data)))
            snapshot_id = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
                INSERT INTO market_snapshots (timestamp, coin, fiat, volume, snapshot_hash, num_exchanges)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, coin, fiat, volume, snapshot_hash, len(quotes_data)))
            snapshot_id = cursor.lastrowid
        
        # Guardar cotizaciones de cada exchange
        for exchange, data in quotes_data.items():
            if isinstance(data, dict):
                ask = data.get('ask')
                bid = data.get('bid')
                total_ask = data.get('totalAsk')
                total_bid = data.get('totalBid')
                api_timestamp = data.get('time')
                
                if self.is_postgres:
                    cursor.execute("""
                        INSERT INTO exchange_quotes 
                        (snapshot_id, exchange, ask, bid, total_ask, total_bid, api_timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (snapshot_id, exchange, ask, bid, total_ask, total_bid, api_timestamp))
                else:
                    cursor.execute("""
                        INSERT INTO exchange_quotes 
                        (snapshot_id, exchange, ask, bid, total_ask, total_bid, api_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (snapshot_id, exchange, ask, bid, total_ask, total_bid, api_timestamp))
        
        # Guardar oportunidades
        for opp in opportunities:
            if self.is_postgres:
                cursor.execute("""
                    INSERT INTO arbitrage_opportunities
                    (snapshot_id, buy_exchange, sell_exchange, buy_price, sell_price, 
                     spread_percentage, profit_per_unit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (snapshot_id, opp.buy_exchange, opp.sell_exchange, opp.buy_price,
                      opp.sell_price, opp.spread_percentage, opp.profit_per_unit))
            else:
                cursor.execute("""
                    INSERT INTO arbitrage_opportunities
                    (snapshot_id, buy_exchange, sell_exchange, buy_price, sell_price, 
                     spread_percentage, profit_per_unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (snapshot_id, opp.buy_exchange, opp.sell_exchange, opp.buy_price,
                      opp.sell_price, opp.spread_percentage, opp.profit_per_unit))
        
        self.conn.commit()
        return snapshot_id
    
    def get_exchange_performance(self, fiat: str = "PEN", days: int = 7) -> List[Dict]:
        """
        Análisis de rendimiento de exchanges
        Responde: ¿En qué exchanges debo tener fondos?
        """
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        param = '%s' if self.is_postgres else '?'
        
        query = f"""
            SELECT 
                ao.buy_exchange as exchange,
                'buy' as role,
                COUNT(*) as times_appeared,
                AVG(ao.spread_percentage) as avg_spread,
                MAX(ao.spread_percentage) as max_spread,
                AVG(ao.profit_per_unit) as avg_profit,
                SUM(ao.profit_per_unit) as total_potential_profit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            WHERE ms.fiat = {param} AND ms.timestamp >= {param}
            GROUP BY ao.buy_exchange
            
            UNION ALL
            
            SELECT 
                ao.sell_exchange as exchange,
                'sell' as role,
                COUNT(*) as times_appeared,
                AVG(ao.spread_percentage) as avg_spread,
                MAX(ao.spread_percentage) as max_spread,
                AVG(ao.profit_per_unit) as avg_profit,
                SUM(ao.profit_per_unit) as total_potential_profit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            WHERE ms.fiat = {param} AND ms.timestamp >= {param}
            GROUP BY ao.sell_exchange
        """
        
        results = cursor.execute(query, (fiat, since_date, fiat, since_date)).fetchall()
        
        # Agrupar por exchange
        exchange_stats = {}
        for row in results:
            exchange = row[0] if self.is_postgres else row['exchange']
            role = row[1] if self.is_postgres else row['role']
            
            if exchange not in exchange_stats:
                exchange_stats[exchange] = {
                    'exchange': exchange,
                    'times_buy': 0,
                    'times_sell': 0,
                    'total_appearances': 0,
                    'avg_spread': 0,
                    'max_spread': 0,
                    'total_potential_profit': 0
                }
            
            times = row[2] if self.is_postgres else row['times_appeared']
            avg_spread = float(row[3]) if self.is_postgres else row['avg_spread']
            max_spread = float(row[4]) if self.is_postgres else row['max_spread']
            total_profit = float(row[6]) if self.is_postgres else row['total_potential_profit']
            
            if role == 'buy':
                exchange_stats[exchange]['times_buy'] = times
            else:
                exchange_stats[exchange]['times_sell'] = times
            
            exchange_stats[exchange]['total_appearances'] += times
            exchange_stats[exchange]['avg_spread'] = max(exchange_stats[exchange]['avg_spread'], avg_spread)
            exchange_stats[exchange]['max_spread'] = max(exchange_stats[exchange]['max_spread'], max_spread)
            exchange_stats[exchange]['total_potential_profit'] += total_profit
        
        result_list = list(exchange_stats.values())
        result_list.sort(key=lambda x: x['total_appearances'], reverse=True)
        
        return result_list
    
    def get_hourly_profitability(self, fiat: str = "PEN", days: int = 7) -> List[Dict]:
        """
        Análisis de rentabilidad por hora
        Responde: ¿A qué horas debo estar activo?
        """
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        param = '%s' if self.is_postgres else '?'
        
        if self.is_postgres:
            hour_extract = "EXTRACT(HOUR FROM ms.timestamp)"
        else:
            hour_extract = "CAST(strftime('%H', ms.timestamp) AS INTEGER)"
        
        query = f"""
            SELECT 
                {hour_extract} as hour,
                COUNT(*) as num_opportunities,
                AVG(ao.spread_percentage) as avg_spread,
                MAX(ao.spread_percentage) as max_spread,
                AVG(ao.profit_per_unit) as avg_profit,
                SUM(ao.profit_per_unit) as total_potential_profit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            WHERE ms.fiat = {param} AND ms.timestamp >= {param}
            GROUP BY {hour_extract}
            ORDER BY hour
        """
        
        results = cursor.execute(query, (fiat, since_date)).fetchall()
        return [dict(row) for row in results]
    
    def get_daily_profitability(self, fiat: str = "PEN", days: int = 30) -> List[Dict]:
        """
        Análisis de rentabilidad por día de semana
        Responde: ¿Qué días son mejores?
        """
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        param = '%s' if self.is_postgres else '?'
        
        if self.is_postgres:
            dow_extract = "EXTRACT(DOW FROM ms.timestamp)"
        else:
            dow_extract = "CAST(strftime('%w', ms.timestamp) AS INTEGER)"
        
        query = f"""
            SELECT 
                {dow_extract} as day_of_week,
                COUNT(*) as num_opportunities,
                AVG(ao.spread_percentage) as avg_spread,
                MAX(ao.spread_percentage) as max_spread,
                SUM(ao.profit_per_unit) as total_potential_profit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            WHERE ms.fiat = {param} AND ms.timestamp >= {param}
            GROUP BY {dow_extract}
            ORDER BY day_of_week
        """
        
        results = cursor.execute(query, (fiat, since_date)).fetchall()
        return [dict(row) for row in results]
    
    def get_exchange_pair_performance(self, fiat: str = "PEN", days: int = 7, limit: int = 20) -> List[Dict]:
        """
        Mejores pares de exchanges
        Responde: ¿Entre qué exchanges arbitrar?
        """
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        param = '%s' if self.is_postgres else '?'
        
        query = f"""
            SELECT 
                ao.buy_exchange,
                ao.sell_exchange,
                ms.coin,
                COUNT(*) as frequency,
                AVG(ao.spread_percentage) as avg_spread,
                MAX(ao.spread_percentage) as max_spread,
                AVG(ao.profit_per_unit) as avg_profit,
                SUM(ao.profit_per_unit) as total_potential_profit
            FROM arbitrage_opportunities ao
            JOIN market_snapshots ms ON ao.snapshot_id = ms.id
            WHERE ms.fiat = {param} AND ms.timestamp >= {param}
            GROUP BY ao.buy_exchange, ao.sell_exchange, ms.coin
            ORDER BY frequency DESC, avg_spread DESC
            LIMIT {param}
        """
        
        results = cursor.execute(query, (fiat, since_date, limit)).fetchall()
        return [dict(row) for row in results]
    
    def get_total_snapshots(self) -> int:
        """Total de snapshots guardados"""
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT COUNT(*) as count FROM market_snapshots").fetchone()
        return result[0] if self.is_postgres else result['count']
    
    def get_total_opportunities(self) -> int:
        """Total de oportunidades guardadas"""
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT COUNT(*) as count FROM arbitrage_opportunities").fetchone()
        return result[0] if self.is_postgres else result['count']
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    print("Inicializando base de datos avanzada...")
    db = ArbitrageDatabaseAdvanced()
    print(f"Tipo: {'PostgreSQL' if db.is_postgres else 'SQLite'}")
    print(f"Snapshots: {db.get_total_snapshots()}")
    print(f"Oportunidades: {db.get_total_opportunities()}")
    db.close()
