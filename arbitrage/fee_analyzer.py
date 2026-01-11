#!/usr/bin/env python3
"""
Analizador de Comisiones - CriptoYa API
Muestra las comisiones de retiro por exchange, criptomoneda y red
"""

import requests
import json
from typing import Dict, Optional
from colorama import init, Fore, Style
import argparse

# Inicializar colorama
init(autoreset=True)

class FeeAnalyzer:
    """Analizador de comisiones de CriptoYa"""
    
    BASE_URL = "https://criptoya.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CriptoYa Fee Analyzer/1.0'
        })
    
    def get_fees(self) -> Optional[Dict]:
        """
        Obtiene todas las comisiones de retiro
        
        Returns:
            Diccionario con comisiones por exchange
        """
        url = f"{self.BASE_URL}/fees"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener comisiones: {e}")
            return None
    
    def display_all_fees(self, fees: Dict):
        """Muestra todas las comisiones de forma organizada"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}📊 COMISIONES DE RETIRO POR EXCHANGE")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        for exchange, coins in sorted(fees.items()):
            print(f"{Fore.YELLOW}🏦 {exchange}")
            print(f"{Fore.CYAN}{'-'*80}")
            
            for coin, networks in sorted(coins.items()):
                if isinstance(networks, dict):
                    print(f"  {Fore.WHITE}💰 {coin}")
                    for network, fee in sorted(networks.items()):
                        print(f"     {Fore.GREEN}├─ {network:<15} {Fore.MAGENTA}{fee} {coin}")
                    print()
            print()
    
    def display_coin_fees(self, fees: Dict, coin: str):
        """Muestra comisiones para una criptomoneda específica"""
        coin = coin.upper()
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}💰 COMISIONES DE RETIRO PARA {coin}")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        found = False
        for exchange, coins in sorted(fees.items()):
            if coin in coins and isinstance(coins[coin], dict):
                found = True
                print(f"{Fore.YELLOW}🏦 {exchange}")
                for network, fee in sorted(coins[coin].items()):
                    print(f"   {Fore.GREEN}├─ {network:<15} {Fore.MAGENTA}{fee} {coin}")
                print()
        
        if not found:
            print(f"{Fore.RED}No se encontraron comisiones para {coin}")
    
    def display_exchange_fees(self, fees: Dict, exchange: str):
        """Muestra comisiones para un exchange específico"""
        # Buscar exchange (case insensitive)
        exchange_data = None
        exchange_name = None
        
        for ex_name, ex_data in fees.items():
            if ex_name.lower() == exchange.lower():
                exchange_data = ex_data
                exchange_name = ex_name
                break
        
        if not exchange_data:
            print(f"{Fore.RED}Exchange '{exchange}' no encontrado")
            print(f"{Fore.YELLOW}Exchanges disponibles: {', '.join(sorted(fees.keys()))}")
            return
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}🏦 COMISIONES DE {exchange_name}")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        for coin, networks in sorted(exchange_data.items()):
            if isinstance(networks, dict):
                print(f"{Fore.WHITE}💰 {coin}")
                for network, fee in sorted(networks.items()):
                    print(f"   {Fore.GREEN}├─ {network:<15} {Fore.MAGENTA}{fee} {coin}")
                print()
    
    def compare_network_fees(self, fees: Dict, coin: str, network: str):
        """Compara comisiones de una red específica entre exchanges"""
        coin = coin.upper()
        network = network.upper()
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}🔍 COMPARACIÓN DE COMISIONES: {coin} en red {network}")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        results = []
        
        for exchange, coins in fees.items():
            if coin in coins and isinstance(coins[coin], dict):
                if network in coins[coin]:
                    fee = coins[coin][network]
                    results.append((exchange, fee))
        
        if not results:
            print(f"{Fore.RED}No se encontraron comisiones para {coin} en red {network}")
            return
        
        # Ordenar por comisión (menor a mayor)
        results.sort(key=lambda x: float(x[1]) if isinstance(x[1], (int, float)) else 0)
        
        print(f"{Fore.WHITE}{'Exchange':<30} {'Comisión':<20}")
        print(f"{Fore.CYAN}{'-'*50}")
        
        for i, (exchange, fee) in enumerate(results, 1):
            if i == 1:
                color = Fore.GREEN  # Mejor opción
                icon = "🥇"
            elif i == 2:
                color = Fore.YELLOW
                icon = "🥈"
            elif i == 3:
                color = Fore.WHITE
                icon = "🥉"
            else:
                color = Fore.WHITE
                icon = "  "
            
            print(f"{color}{icon} {exchange:<28} {fee} {coin}")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Analizador de Comisiones de CriptoYa API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python fee_analyzer.py                           # Ver todas las comisiones
  python fee_analyzer.py --coin BTC                # Ver comisiones de BTC
  python fee_analyzer.py --exchange "Binance P2P"  # Ver comisiones de un exchange
  python fee_analyzer.py --compare BTC BITCOIN     # Comparar comisiones de BTC en red Bitcoin
        """
    )
    
    parser.add_argument(
        '--coin', '-c',
        type=str,
        help='Mostrar comisiones para una criptomoneda específica'
    )
    
    parser.add_argument(
        '--exchange', '-e',
        type=str,
        help='Mostrar comisiones para un exchange específico'
    )
    
    parser.add_argument(
        '--compare',
        nargs=2,
        metavar=('COIN', 'NETWORK'),
        help='Comparar comisiones de una moneda en una red específica entre exchanges'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Mostrar resultado en formato JSON'
    )
    
    args = parser.parse_args()
    
    analyzer = FeeAnalyzer()
    fees = analyzer.get_fees()
    
    if not fees:
        print(f"{Fore.RED}No se pudieron obtener las comisiones")
        return
    
    if args.json:
        print(json.dumps(fees, indent=2))
    elif args.compare:
        coin, network = args.compare
        analyzer.compare_network_fees(fees, coin, network)
    elif args.coin:
        analyzer.display_coin_fees(fees, args.coin)
    elif args.exchange:
        analyzer.display_exchange_fees(fees, args.exchange)
    else:
        analyzer.display_all_fees(fees)

if __name__ == "__main__":
    main()
