#!/usr/bin/env python3
"""
Script de Monitoreo de Arbitraje - CriptoYa API
Monitorea spreads y rutas de arbitraje en tiempo real
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from colorama import init, Fore, Back, Style
import os

try:
    from arbitrage_db import ArbitrageDatabase
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from arbitrage_db_advanced import ArbitrageDatabaseAdvanced
    DB_ADVANCED_AVAILABLE = True
except ImportError:
    DB_ADVANCED_AVAILABLE = False

# Inicializar colorama para colores en terminal
init(autoreset=True)

@dataclass
class ArbitrageOpportunity:
    """Representa una oportunidad de arbitraje"""
    coin: str
    fiat: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_percentage: float
    profit_per_unit: float
    timestamp: datetime

class CriptoYaArbitrageMonitor:
    """Monitor de arbitraje para CriptoYa API"""
    
    BASE_URL = "https://criptoya.com/api"
    FEES_CACHE = None
    FEES_CACHE_TIME = None
    FEES_CACHE_DURATION = 3600  # Cache fees for 1 hour
    
    # Configuración de monedas y exchanges a monitorear
    # IMPORTANTE: Reducido para evitar rate limiting de la API
    COINS = ["BTC", "ETH", "USDT", "USDC"]  # Monedas más populares
    FIATS = ["ARS", "USD"]  # Monedas fiat principales
    VOLUME = 1.0  # Volumen para consultar
    
    # Umbral mínimo de spread para considerar una oportunidad (%)
    MIN_SPREAD_THRESHOLD = 0.5
    
    # Delay entre peticiones para evitar rate limiting (segundos)
    REQUEST_DELAY = 0.5
    
    def __init__(self, min_spread: float = 0.5, update_interval: int = 30, request_delay: float = 0.5, save_to_db: bool = False, db_path: str = "arbitrage_opportunities.db", use_advanced_db: bool = False):
        """
        Inicializa el monitor de arbitraje
        
        Args:
            min_spread: Spread mínimo en porcentaje para mostrar oportunidades
            update_interval: Intervalo de actualización en segundos (mínimo 30s recomendado)
            request_delay: Delay entre peticiones a la API en segundos
            save_to_db: Si True, guarda oportunidades en base de datos
            db_path: Ruta al archivo de base de datos
            use_advanced_db: Si True, usa esquema avanzado con snapshots completos
        """
        self.min_spread = min_spread
        self.update_interval = max(update_interval, 30)  # Mínimo 30 segundos
        self.request_delay = request_delay
        self.save_to_db = save_to_db
        self.use_advanced_db = use_advanced_db
        self.db = None
        self.db_advanced = None
        
        if self.save_to_db:
            if use_advanced_db and DB_ADVANCED_AVAILABLE:
                self.db_advanced = ArbitrageDatabaseAdvanced(db_path=db_path)
                print(f"{Fore.GREEN}✓ Base de datos AVANZADA habilitada: {db_path}")
            elif DB_AVAILABLE:
                self.db = ArbitrageDatabase(db_path)
                print(f"{Fore.GREEN}✓ Base de datos habilitada: {db_path}")
            else:
                print(f"{Fore.YELLOW}⚠️  Módulo de base de datos no disponible. Continuando sin guardar.")
                self.save_to_db = False
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CriptoYa Arbitrage Monitor/1.0'
        })
        
    def get_fees(self) -> Optional[Dict]:
        """
        Obtiene información de comisiones de retiro por exchange y red
        Usa cache para evitar consultas excesivas
        
        Returns:
            Diccionario con comisiones por exchange, coin y red
        """
        # Verificar cache
        if (self.FEES_CACHE and self.FEES_CACHE_TIME and 
            time.time() - self.FEES_CACHE_TIME < self.FEES_CACHE_DURATION):
            return self.FEES_CACHE
        
        url = f"{self.BASE_URL}/fees"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.FEES_CACHE = response.json()
            self.FEES_CACHE_TIME = time.time()
            return self.FEES_CACHE
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener comisiones: {e}")
            return None
    
    def get_quotes(self, coin: str, fiat: str, volume: float = 1.0) -> Optional[Dict]:
        """
        Obtiene cotizaciones de todos los exchanges para un par específico
        
        Args:
            coin: Criptomoneda (ej: BTC, ETH)
            fiat: Moneda fiat (ej: ARS, USD)
            volume: Volumen a consultar
            
        Returns:
            Diccionario con cotizaciones por exchange o None si hay error
        """
        url = f"{self.BASE_URL}/{coin}/{fiat}/{volume}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener cotizaciones para {coin}/{fiat}: {e}")
            return None
    
    def calculate_spreads(self, quotes: Dict, coin: str, fiat: str) -> List[ArbitrageOpportunity]:
        """
        Calcula spreads entre diferentes exchanges
        
        Args:
            quotes: Diccionario con cotizaciones por exchange
            coin: Criptomoneda
            fiat: Moneda fiat
            
        Returns:
            Lista de oportunidades de arbitraje ordenadas por spread
        """
        opportunities = []
        exchanges_data = []
        
        # Extraer datos de cada exchange
        for exchange, data in quotes.items():
            if isinstance(data, dict) and 'totalBid' in data and 'totalAsk' in data:
                # totalBid: precio al que puedes vender (lo que te pagan)
                # totalAsk: precio al que puedes comprar (lo que pagas)
                if data['totalBid'] and data['totalAsk']:
                    exchanges_data.append({
                        'exchange': exchange,
                        'bid': float(data['totalBid']),  # Precio de venta
                        'ask': float(data['totalAsk']),  # Precio de compra
                        'time': data.get('time', int(time.time()))
                    })
        
        # Calcular spreads entre todos los pares de exchanges
        for i, buy_exchange in enumerate(exchanges_data):
            for sell_exchange in exchanges_data[i+1:]:
                # Comprar en exchange con menor ask, vender en exchange con mayor bid
                if buy_exchange['ask'] < sell_exchange['bid']:
                    buy_price = buy_exchange['ask']
                    sell_price = sell_exchange['bid']
                    buy_name = buy_exchange['exchange']
                    sell_name = sell_exchange['exchange']
                elif sell_exchange['ask'] < buy_exchange['bid']:
                    buy_price = sell_exchange['ask']
                    sell_price = buy_exchange['bid']
                    buy_name = sell_exchange['exchange']
                    sell_name = buy_exchange['exchange']
                else:
                    continue
                
                # Calcular spread y ganancia
                spread = ((sell_price - buy_price) / buy_price) * 100
                profit = sell_price - buy_price
                
                if spread >= self.min_spread:
                    opportunity = ArbitrageOpportunity(
                        coin=coin,
                        fiat=fiat,
                        buy_exchange=buy_name,
                        sell_exchange=sell_name,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        spread_percentage=spread,
                        profit_per_unit=profit,
                        timestamp=datetime.now()
                    )
                    opportunities.append(opportunity)
        
        # Ordenar por spread descendente
        opportunities.sort(key=lambda x: x.spread_percentage, reverse=True)
        return opportunities
    
    def display_opportunities(self, opportunities: List[ArbitrageOpportunity], top_n: int = 10):
        """
        Muestra las mejores oportunidades de arbitraje en consola
        
        Args:
            opportunities: Lista de oportunidades
            top_n: Número de oportunidades a mostrar
        """
        # Limpiar pantalla
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Encabezado
        print(f"\n{Back.BLUE}{Fore.WHITE} 📊 MONITOR DE ARBITRAJE CRIPTOYA {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}Umbral mínimo de spread: {self.min_spread}%")
        print(f"{Fore.CYAN}Intervalo de actualización: {self.update_interval}s")
        print(f"{Fore.CYAN}Delay entre peticiones: {self.request_delay}s")
        print(f"{Fore.GREEN}✓ Los precios YA INCLUYEN todas las comisiones (trading + transferencia)\n")
        
        if not opportunities:
            print(f"{Fore.YELLOW}⚠️  No se encontraron oportunidades de arbitraje con spread >= {self.min_spread}%")
            return
        
        # Mostrar top oportunidades
        print(f"{Back.GREEN}{Fore.BLACK} 🚀 TOP {min(top_n, len(opportunities))} OPORTUNIDADES DE ARBITRAJE {Style.RESET_ALL}\n")
        
        for i, opp in enumerate(opportunities[:top_n], 1):
            # Color según el spread
            if opp.spread_percentage >= 5:
                color = Fore.GREEN
                icon = "🔥"
            elif opp.spread_percentage >= 2:
                color = Fore.YELLOW
                icon = "⭐"
            else:
                color = Fore.WHITE
                icon = "💡"
            
            print(f"{color}{icon} #{i} {opp.coin}/{opp.fiat}")
            print(f"   Comprar en:  {Fore.CYAN}{opp.buy_exchange:<20}{color} @ {opp.buy_price:,.2f} {opp.fiat} (con comisiones)")
            print(f"   Vender en:   {Fore.MAGENTA}{opp.sell_exchange:<20}{color} @ {opp.sell_price:,.2f} {opp.fiat} (con comisiones)")
            print(f"   {Fore.GREEN}Spread: {opp.spread_percentage:.2f}% | Ganancia neta: {opp.profit_per_unit:,.2f} {opp.fiat}{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⚠️  Considera tiempo de transferencia entre exchanges{Style.RESET_ALL}")
            print()
        
        # Resumen
        total_opportunities = len(opportunities)
        avg_spread = sum(o.spread_percentage for o in opportunities) / total_opportunities
        max_spread = opportunities[0].spread_percentage if opportunities else 0
        
        print(f"{Fore.CYAN}{'─' * 80}")
        print(f"📈 Resumen: {total_opportunities} oportunidades | Spread promedio: {avg_spread:.2f}% | Spread máximo: {max_spread:.2f}%")
        print(f"{Fore.CYAN}{'─' * 80}\n")
    
    def scan_all_markets(self) -> List[ArbitrageOpportunity]:
        """
        Escanea todos los mercados configurados en busca de oportunidades
        
        Returns:
            Lista de todas las oportunidades encontradas
        """
        all_opportunities = []
        
        for coin in self.COINS:
            for fiat in self.FIATS:
                quotes = self.get_quotes(coin, fiat, self.VOLUME)
                
                if quotes:
                    opportunities = self.calculate_spreads(quotes, coin, fiat)
                    all_opportunities.extend(opportunities)
                
                # Pausa entre peticiones para respetar rate limiting
                time.sleep(self.request_delay)
        
        # Ordenar todas las oportunidades por spread
        all_opportunities.sort(key=lambda x: x.spread_percentage, reverse=True)
        
        # Guardar en base de datos si está habilitado
        if self.save_to_db and self.db and all_opportunities:
            saved_count = self.db.save_opportunities(all_opportunities)
            print(f"{Fore.GREEN}✓ Guardadas {saved_count} oportunidades en BD")
        
        return all_opportunities
    
    def run(self):
        """
        Ejecuta el monitor en modo continuo
        """
        print(f"{Fore.GREEN}🚀 Iniciando Monitor de Arbitraje CriptoYa...")
        print(f"{Fore.CYAN}Presiona Ctrl+C para detener\n")
        
        try:
            while True:
                # Escanear mercados
                opportunities = self.scan_all_markets()
                
                # Mostrar resultados
                self.display_opportunities(opportunities)
                
                # Esperar antes de la siguiente actualización
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Monitor detenido por el usuario")
            if self.db:
                total = self.db.get_total_opportunities()
                print(f"{Fore.CYAN}💾 Total de oportunidades guardadas: {total}")
                self.db.close()
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error inesperado: {e}")
            if self.db:
                self.db.close()

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor de Arbitraje para CriptoYa API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python arbitrage_monitor.py                    # Ejecutar con valores por defecto
  python arbitrage_monitor.py --spread 1.0       # Spread mínimo de 1%
  python arbitrage_monitor.py --interval 5       # Actualizar cada 5 segundos
  python arbitrage_monitor.py --spread 2 -i 15   # Spread 2% y actualización cada 15s
        """
    )
    
    parser.add_argument(
        '--spread', '-s',
        type=float,
        default=0.5,
        help='Spread mínimo en porcentaje para mostrar oportunidades (default: 0.5)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Intervalo de actualización en segundos (mínimo 30s recomendado, default: 30)'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=0.5,
        help='Delay entre peticiones a la API en segundos (default: 0.5)'
    )
    
    parser.add_argument(
        '--coins', '-c',
        nargs='+',
        help='Lista de criptomonedas a monitorear (default: BTC ETH USDT USDC DAI BNB SOL DOGE ADA MATIC)'
    )
    
    parser.add_argument(
        '--fiats', '-f',
        nargs='+',
        help='Lista de monedas fiat a monitorear (default: ARS USD)'
    )
    
    parser.add_argument(
        '--save-db',
        action='store_true',
        help='Guardar oportunidades en base de datos para análisis posterior'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='arbitrage_opportunities.db',
        help='Ruta al archivo de base de datos (default: arbitrage_opportunities.db)'
    )
    
    args = parser.parse_args()
    
    # Crear monitor
    monitor = CriptoYaArbitrageMonitor(
        min_spread=args.spread,
        update_interval=args.interval,
        request_delay=args.delay,
        save_to_db=args.save_db,
        db_path=args.db_path
    )
    
    # Configurar monedas personalizadas si se especificaron
    if args.coins:
        monitor.COINS = args.coins
    if args.fiats:
        monitor.FIATS = args.fiats
    
    # Ejecutar monitor
    monitor.run()

if __name__ == "__main__":
    main()
