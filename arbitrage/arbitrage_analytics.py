#!/usr/bin/env python3
"""
Analizador de Oportunidades Históricas
Analiza la base de datos para recomendar distribución de fondos
"""

import argparse
from colorama import init, Fore, Style
from arbitrage_db import ArbitrageDatabase
from datetime import datetime

# Inicializar colorama
init(autoreset=True)

def display_exchange_recommendations(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Muestra recomendaciones de exchanges para distribuir fondos"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}💰 RECOMENDACIONES DE DISTRIBUCIÓN DE FONDOS - {fiat}")
    print(f"{Fore.CYAN}Análisis de los últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    stats = db.get_exchange_statistics(fiat, days)
    
    if not stats:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes para {fiat}")
        print(f"{Fore.CYAN}💡 Ejecuta el monitor con --save-db para empezar a recopilar datos\n")
        return
    
    print(f"{Fore.WHITE}{'Exchange':<25} {'Compras':<12} {'Ventas':<12} {'Total':<10} {'Spread Prom':<15}")
    print(f"{Fore.CYAN}{'-'*80}")
    
    for i, stat in enumerate(stats[:15], 1):
        # Determinar importancia
        if i <= 3:
            color = Fore.GREEN
            icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        elif i <= 5:
            color = Fore.YELLOW
            icon = "⭐"
        else:
            color = Fore.WHITE
            icon = "  "
        
        print(f"{color}{icon} {stat['exchange']:<23} "
              f"{stat['times_best_buy']:<12} "
              f"{stat['times_best_sell']:<12} "
              f"{stat['total_opportunities']:<10} "
              f"{stat['avg_spread']:.2f}%")
    
    print(f"\n{Fore.GREEN}📊 INTERPRETACIÓN:")
    print(f"{Fore.WHITE}• {Fore.CYAN}Compras{Fore.WHITE}: Veces que este exchange tuvo el mejor precio de compra")
    print(f"{Fore.WHITE}• {Fore.MAGENTA}Ventas{Fore.WHITE}: Veces que este exchange tuvo el mejor precio de venta")
    print(f"{Fore.WHITE}• {Fore.GREEN}Total{Fore.WHITE}: Total de oportunidades donde apareció este exchange")
    
    print(f"\n{Fore.YELLOW}💡 RECOMENDACIÓN:")
    top_3 = stats[:3]
    print(f"{Fore.WHITE}Para maximizar oportunidades de arbitraje en {fiat}, considera tener fondos en:")
    for i, stat in enumerate(top_3, 1):
        print(f"{Fore.GREEN}  {i}. {stat['exchange']}")
    print()

def display_best_pairs(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Muestra los mejores pares de exchanges para arbitraje"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}🔄 MEJORES RUTAS DE ARBITRAJE - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    pairs = db.get_best_pairs(fiat, days, limit=10)
    
    if not pairs:
        print(f"{Fore.YELLOW}⚠️  No hay datos de pares para {fiat}\n")
        return
    
    for i, pair in enumerate(pairs, 1):
        if i <= 3:
            color = Fore.GREEN
            icon = "🔥"
        else:
            color = Fore.WHITE
            icon = "💡"
        
        print(f"{color}{icon} #{i} {pair['coin']}")
        print(f"   Comprar en:  {Fore.CYAN}{pair['buy_exchange']:<30}")
        print(f"   Vender en:   {Fore.MAGENTA}{pair['sell_exchange']:<30}")
        print(f"   {Fore.WHITE}Frecuencia: {pair['frequency']} veces | "
              f"Spread prom: {pair['avg_spread']:.2f}% | "
              f"Ganancia prom: {pair['avg_profit']:.2f} {fiat}")
        print()

def display_coin_statistics(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Muestra estadísticas por criptomoneda"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}📈 ESTADÍSTICAS POR CRIPTOMONEDA - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    coins = db.get_coin_statistics(fiat, days)
    
    if not coins:
        print(f"{Fore.YELLOW}⚠️  No hay datos de monedas para {fiat}\n")
        return
    
    print(f"{Fore.WHITE}{'Moneda':<10} {'Oportunidades':<15} {'Spread Prom':<15} {'Spread Máx':<15}")
    print(f"{Fore.CYAN}{'-'*60}")
    
    for coin in coins:
        print(f"{Fore.GREEN}{coin['coin']:<10} "
              f"{Fore.WHITE}{coin['opportunities_count']:<15} "
              f"{coin['avg_spread']:.2f}%{' '*10} "
              f"{coin['max_spread']:.2f}%")
    
    print(f"\n{Fore.YELLOW}💡 TIP:")
    best_coin = coins[0]
    print(f"{Fore.WHITE}La moneda con más oportunidades es {Fore.GREEN}{best_coin['coin']}{Fore.WHITE} "
          f"con {best_coin['opportunities_count']} oportunidades detectadas\n")

def display_recent_opportunities(db: ArbitrageDatabase, fiat: str = "PEN", hours: int = 24):
    """Muestra oportunidades recientes"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}🕐 OPORTUNIDADES RECIENTES - {fiat}")
    print(f"{Fore.CYAN}Últimas {hours} horas")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    opportunities = db.get_recent_opportunities(fiat, hours, limit=20)
    
    if not opportunities:
        print(f"{Fore.YELLOW}⚠️  No hay oportunidades recientes para {fiat}\n")
        return
    
    for i, opp in enumerate(opportunities[:10], 1):
        timestamp = datetime.fromisoformat(opp['timestamp'])
        time_str = timestamp.strftime('%H:%M:%S')
        
        if opp['spread_percentage'] >= 2:
            color = Fore.GREEN
            icon = "🔥"
        else:
            color = Fore.WHITE
            icon = "💡"
        
        print(f"{color}{icon} [{time_str}] {opp['coin']}/{fiat}")
        print(f"   {opp['buy_exchange']} → {opp['sell_exchange']}")
        print(f"   Spread: {opp['spread_percentage']:.2f}% | Ganancia: {opp['profit_per_unit']:.2f} {fiat}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Analizador de Oportunidades de Arbitraje',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python arbitrage_analytics.py --fiat PEN              # Análisis completo para PEN
  python arbitrage_analytics.py --fiat ARS --days 30   # Análisis de 30 días para ARS
  python arbitrage_analytics.py --exchanges-only       # Solo recomendaciones de exchanges
  python arbitrage_analytics.py --recent               # Solo oportunidades recientes
        """
    )
    
    parser.add_argument(
        '--fiat',
        type=str,
        default='PEN',
        help='Moneda fiat a analizar (default: PEN)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Días hacia atrás a analizar (default: 7)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='arbitrage_opportunities.db',
        help='Ruta al archivo de base de datos'
    )
    
    parser.add_argument(
        '--exchanges-only',
        action='store_true',
        help='Mostrar solo recomendaciones de exchanges'
    )
    
    parser.add_argument(
        '--pairs-only',
        action='store_true',
        help='Mostrar solo mejores pares de arbitraje'
    )
    
    parser.add_argument(
        '--coins-only',
        action='store_true',
        help='Mostrar solo estadísticas de monedas'
    )
    
    parser.add_argument(
        '--recent',
        action='store_true',
        help='Mostrar solo oportunidades recientes'
    )
    
    args = parser.parse_args()
    
    # Abrir base de datos
    try:
        db = ArbitrageDatabase(args.db_path)
    except Exception as e:
        print(f"{Fore.RED}❌ Error al abrir base de datos: {e}")
        print(f"{Fore.YELLOW}💡 Asegúrate de ejecutar el monitor con --save-db primero")
        return
    
    total = db.get_total_opportunities()
    
    if total == 0:
        print(f"\n{Fore.YELLOW}⚠️  La base de datos está vacía")
        print(f"{Fore.CYAN}💡 Ejecuta el monitor con --save-db para empezar a recopilar datos:")
        print(f"{Fore.WHITE}   python arbitrage_monitor.py --fiats {args.fiat} --save-db\n")
        db.close()
        return
    
    print(f"\n{Fore.GREEN}📊 Base de datos: {total} oportunidades registradas")
    
    # Mostrar análisis según flags
    if args.exchanges_only:
        display_exchange_recommendations(db, args.fiat, args.days)
    elif args.pairs_only:
        display_best_pairs(db, args.fiat, args.days)
    elif args.coins_only:
        display_coin_statistics(db, args.fiat, args.days)
    elif args.recent:
        display_recent_opportunities(db, args.fiat, 24)
    else:
        # Mostrar todo
        display_exchange_recommendations(db, args.fiat, args.days)
        display_best_pairs(db, args.fiat, args.days)
        display_coin_statistics(db, args.fiat, args.days)
    
    db.close()

if __name__ == "__main__":
    main()
