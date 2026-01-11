#!/usr/bin/env python3
"""
Módulo de Base de Datos para Arbitraje - Soporte PostgreSQL
Guarda y analiza oportunidades de arbitraje históricas
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

# Intentar importar PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# SQLite como fallback
import sqlite3

@dataclass
class OpportunityRecord:
    """Registro de oportunidad de arbitraje"""
    id: Optional[int]
    timestamp: datetime
    coin: str
    fiat: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_percentage: float
    profit_per_unit: float

class ArbitrageDatabase:
    """Gestor de base de datos para oportunidades de arbitraje"""
    
    def __init__(self, db_url: Optional[str] = None, db_path: str = "arbitrage_opportunities.db"):
        """
        Inicializa la base de datos
        
        Args:
            db_url: URL de PostgreSQL (ej: postgresql://user:pass@host:5432/dbname)
                   Si es None, usa SQLite
            db_path: Ruta al archivo SQLite (solo si db_url es None)
        """
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
            print(f"✓ Conectado a PostgreSQL")
        except Exception as e:
            print(f"⚠️  Error conectando a PostgreSQL: {e}")
            print(f"   Usando SQLite como fallback")
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Inicializa SQLite"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.is_postgres = False
        self._create_sqlite_tables()
    
    def _create_postgres_tables(self):
        """Crea tablas en PostgreSQL"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                coin VARCHAR(20) NOT NULL,
                fiat VARCHAR(10) NOT NULL,
                buy_exchange VARCHAR(100) NOT NULL,
                sell_exchange VARCHAR(100) NOT NULL,
                buy_price DECIMAL(20, 8) NOT NULL,
                sell_price DECIMAL(20, 8) NOT NULL,
                spread_percentage DECIMAL(10, 4) NOT NULL,
                profit_per_unit DECIMAL(20, 8) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON opportunities(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_coin_fiat 
            ON opportunities(coin, fiat)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exchanges 
            ON opportunities(buy_exchange, sell_exchange)
        """)
        
        self.conn.commit()
    
    def _create_sqlite_tables(self):
        """Crea tablas en SQLite"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                coin TEXT NOT NULL,
                fiat TEXT NOT NULL,
                buy_exchange TEXT NOT NULL,
                sell_exchange TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                spread_percentage REAL NOT NULL,
                profit_per_unit REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON opportunities(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_coin_fiat 
            ON opportunities(coin, fiat)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exchanges 
            ON opportunities(buy_exchange, sell_exchange)
        """)
        
        self.conn.commit()
    
    def save_opportunity(self, opportunity) -> int:
        """Guarda una oportunidad en la base de datos"""
        cursor = self.conn.cursor()
        
        if self.is_postgres:
            cursor.execute("""
                INSERT INTO opportunities 
                (timestamp, coin, fiat, buy_exchange, sell_exchange, 
                 buy_price, sell_price, spread_percentage, profit_per_unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                opportunity.timestamp,
                opportunity.coin,
                opportunity.fiat,
                opportunity.buy_exchange,
                opportunity.sell_exchange,
                opportunity.buy_price,
                opportunity.sell_price,
                opportunity.spread_percentage,
                opportunity.profit_per_unit
            ))
            result = cursor.fetchone()
            self.conn.commit()
            return result[0] if result else None
        else:
            cursor.execute("""
                INSERT INTO opportunities 
                (timestamp, coin, fiat, buy_exchange, sell_exchange, 
                 buy_price, sell_price, spread_percentage, profit_per_unit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity.timestamp,
                opportunity.coin,
                opportunity.fiat,
                opportunity.buy_exchange,
                opportunity.sell_exchange,
                opportunity.buy_price,
                opportunity.sell_price,
                opportunity.spread_percentage,
                opportunity.profit_per_unit
            ))
            self.conn.commit()
            return cursor.lastrowid
    
    def save_opportunities(self, opportunities: List) -> int:
        """Guarda múltiples oportunidades"""
        count = 0
        for opp in opportunities:
            self.save_opportunity(opp)
            count += 1
        return count
    
    def get_exchange_statistics(self, fiat: str = "PEN", days: int = 7) -> List[Dict]:
        """Obtiene estadísticas de exchanges"""
        cursor = self.conn.cursor() if self.is_postgres else self.conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Usar parámetros según el tipo de BD
        param = '%s' if self.is_postgres else '?'
        
        # Estadísticas de compra
        buy_stats = cursor.execute(f"""
            SELECT 
                buy_exchange as exchange,
                COUNT(*) as times_best_buy,
                AVG(spread_percentage) as avg_spread,
                MAX(spread_percentage) as max_spread,
                AVG(profit_per_unit) as avg_profit
            FROM opportunities
            WHERE fiat = {param} AND timestamp >= {param}
            GROUP BY buy_exchange
            ORDER BY times_best_buy DESC
        """, (fiat, since_date)).fetchall()
        
        # Estadísticas de venta
        sell_stats = cursor.execute(f"""
            SELECT 
                sell_exchange as exchange,
                COUNT(*) as times_best_sell,
                AVG(spread_percentage) as avg_spread,
                MAX(spread_percentage) as max_spread,
                AVG(profit_per_unit) as avg_profit
            FROM opportunities
            WHERE fiat = {param} AND timestamp >= {param}
            GROUP BY sell_exchange
            ORDER BY times_best_sell DESC
        """, (fiat, since_date)).fetchall()
        
        # Combinar estadísticas
        exchange_stats = {}
        
        for row in buy_stats:
            exchange = row['exchange'] if self.is_postgres else row['exchange']
            exchange_stats[exchange] = {
                'exchange': exchange,
                'times_best_buy': row['times_best_buy'] if self.is_postgres else row['times_best_buy'],
                'times_best_sell': 0,
                'total_opportunities': row['times_best_buy'] if self.is_postgres else row['times_best_buy'],
                'avg_spread': float(row['avg_spread']) if self.is_postgres else row['avg_spread'],
                'max_spread': float(row['max_spread']) if self.is_postgres else row['max_spread'],
                'avg_profit': float(row['avg_profit']) if self.is_postgres else row['avg_profit']
            }
        
        for row in sell_stats:
            exchange = row['exchange'] if self.is_postgres else row['exchange']
            if exchange in exchange_stats:
                exchange_stats[exchange]['times_best_sell'] = row['times_best_sell'] if self.is_postgres else row['times_best_sell']
                exchange_stats[exchange]['total_opportunities'] += row['times_best_sell'] if self.is_postgres else row['times_best_sell']
            else:
                exchange_stats[exchange] = {
                    'exchange': exchange,
                    'times_best_buy': 0,
                    'times_best_sell': row['times_best_sell'] if self.is_postgres else row['times_best_sell'],
                    'total_opportunities': row['times_best_sell'] if self.is_postgres else row['times_best_sell'],
                    'avg_spread': float(row['avg_spread']) if self.is_postgres else row['avg_spread'],
                    'max_spread': float(row['max_spread']) if self.is_postgres else row['max_spread'],
                    'avg_profit': float(row['avg_profit']) if self.is_postgres else row['avg_profit']
                }
        
        stats_list = list(exchange_stats.values())
        stats_list.sort(key=lambda x: x['total_opportunities'], reverse=True)
        
        return stats_list
    
    def get_best_pairs(self, fiat: str = "PEN", days: int = 7, limit: int = 10) -> List[Dict]:
        """Obtiene los mejores pares de exchanges"""
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        
        param = '%s' if self.is_postgres else '?'
        
        results = cursor.execute(f"""
            SELECT 
                buy_exchange,
                sell_exchange,
                coin,
                COUNT(*) as frequency,
                AVG(spread_percentage) as avg_spread,
                MAX(spread_percentage) as max_spread,
                AVG(profit_per_unit) as avg_profit,
                MAX(profit_per_unit) as max_profit
            FROM opportunities
            WHERE fiat = {param} AND timestamp >= {param}
            GROUP BY buy_exchange, sell_exchange, coin
            ORDER BY frequency DESC, avg_spread DESC
            LIMIT {param}
        """, (fiat, since_date, limit)).fetchall()
        
        return [dict(row) for row in results]
    
    def get_coin_statistics(self, fiat: str = "PEN", days: int = 7) -> List[Dict]:
        """Obtiene estadísticas por criptomoneda"""
        cursor = self.conn.cursor()
        since_date = datetime.now() - timedelta(days=days)
        
        param = '%s' if self.is_postgres else '?'
        
        results = cursor.execute(f"""
            SELECT 
                coin,
                COUNT(*) as opportunities_count,
                AVG(spread_percentage) as avg_spread,
                MAX(spread_percentage) as max_spread,
                AVG(profit_per_unit) as avg_profit,
                MAX(profit_per_unit) as max_profit
            FROM opportunities
            WHERE fiat = {param} AND timestamp >= {param}
            GROUP BY coin
            ORDER BY opportunities_count DESC
        """, (fiat, since_date)).fetchall()
        
        return [dict(row) for row in results]
    
    def get_recent_opportunities(self, fiat: str = "PEN", hours: int = 24, limit: int = 50) -> List[Dict]:
        """Obtiene oportunidades recientes"""
        cursor = self.conn.cursor()
        since_time = datetime.now() - timedelta(hours=hours)
        
        param = '%s' if self.is_postgres else '?'
        
        results = cursor.execute(f"""
            SELECT *
            FROM opportunities
            WHERE fiat = {param} AND timestamp >= {param}
            ORDER BY spread_percentage DESC
            LIMIT {param}
        """, (fiat, since_time, limit)).fetchall()
        
        return [dict(row) for row in results]
    
    def get_total_opportunities(self) -> int:
        """Obtiene el total de oportunidades guardadas"""
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT COUNT(*) as count FROM opportunities").fetchone()
        return result['count'] if self.is_postgres else result['count']
    
    def close(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    print("Inicializando base de datos...")
    db = ArbitrageDatabase()
    print(f"Tipo de BD: {'PostgreSQL' if db.is_postgres else 'SQLite'}")
    print(f"Total de oportunidades: {db.get_total_opportunities()}")
    db.close()
    print("✓ Base de datos inicializada correctamente")
