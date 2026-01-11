#!/usr/bin/env python3
"""
Análisis Profesional de Arbitraje
Herramienta completa para decidir dónde distribuir fondos y cuándo operar
"""

import argparse
from datetime import datetime
from colorama import init, Fore, Style
from arbitrage_db_advanced import ArbitrageDatabaseAdvanced

init(autoreset=True)

def display_exchange_recommendations(db: ArbitrageDatabaseAdvanced, fiat: str = "PEN", days: int = 7):
    """Recomendaciones de exchanges para distribuir fondos"""
    
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.GREEN}💰 RECOMENDACIÓN: ¿EN QUÉ EXCHANGES METER MIS FONDOS? - {fiat}")
    print(f"{Fore.CYAN}Análisis de los últimos {days} días")
    print(f"{Fore.CYAN}{'='*90}\n")
    
    stats = db.get_exchange_performance(fiat, days)
    
    if not stats:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes. Ejecuta el monitor con --save-db --use-advanced-db\n")
        return
    
    print(f"{Fore.WHITE}{'Exchange':<30} {'Compras':<10} {'Ventas':<10} {'Total':<10} {'Ganancia Potencial':<20}")
    print(f"{Fore.CYAN}{'-'*90}")
    
    for i, stat in enumerate(stats[:10], 1):
        if i <= 3:
            color = Fore.GREEN
            icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        else:
            color = Fore.WHITE
            icon = "  "
        
        print(f"{color}{icon} {stat['exchange']:<28} "
              f"{stat['times_buy']:<10} "
              f"{stat['times_sell']:<10} "
              f"{stat['total_appearances']:<10} "
              f"{stat['total_potential_profit']:,.2f} {fiat}")
    
    print(f"\n{Fore.GREEN}💡 RECOMENDACIÓN DE DISTRIBUCIÓN:")
    top_3 = stats[:3]
    total_appearances = sum(s['total_appearances'] for s in top_3)
    
    for i, stat in enumerate(top_3, 1):
        percentage = (stat['total_appearances'] / total_appearances * 100) if total_appearances > 0 else 0
        print(f"{Fore.WHITE}  {i}. {Fore.CYAN}{stat['exchange']:<30} {Fore.WHITE}→ {Fore.GREEN}{percentage:.1f}% de tus fondos")
    
    print(f"\n{Fore.YELLOW}📊 INTERPRETACIÓN:")
    print(f"{Fore.WHITE}  • Compras: Veces que apareció como mejor precio de COMPRA")
    print(f"{Fore.WHITE}  • Ventas: Veces que apareció como mejor precio de VENTA")
    print(f"{Fore.WHITE}  • Total: Total de oportunidades donde este exchange fue útil")
    print()

def display_hourly_analysis(db: ArbitrageDatabaseAdvanced, fiat: str = "PEN", days: int = 7):
    """Análisis de mejores horas para operar"""
    
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.GREEN}⏰ ANÁLISIS: ¿A QUÉ HORAS DEBO ESTAR ACTIVO? - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*90}\n")
    
    hourly = db.get_hourly_profitability(fiat, days)
    
    if not hourly:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    # Encontrar mejor hora
    best_hour = max(hourly, key=lambda x: x['num_opportunities'])
    
    print(f"{Fore.WHITE}{'Hora':<10} {'Oportunidades':<15} {'Spread Prom':<15} {'Ganancia Total':<20}")
    print(f"{Fore.CYAN}{'-'*70}")
    
    for hour_data in hourly:
        hour = int(hour_data['hour'])
        num_opps = hour_data['num_opportunities']
        avg_spread = hour_data['avg_spread']
        total_profit = hour_data['total_potential_profit']
        
        if num_opps >= best_hour['num_opportunities'] * 0.7:
            color = Fore.GREEN
            icon = "🔥"
        elif num_opps >= best_hour['num_opportunities'] * 0.4:
            color = Fore.YELLOW
            icon = "⭐"
        else:
            color = Fore.WHITE
            icon = "  "
        
        print(f"{color}{icon} {hour:02d}:00{' '*4} {num_opps:<15} {avg_spread:.2f}%{' '*9} {total_profit:,.2f} {fiat}")
    
    print(f"\n{Fore.GREEN}💡 RECOMENDACIÓN:")
    top_hours = sorted(hourly, key=lambda x: x['num_opportunities'], reverse=True)[:3]
    print(f"{Fore.WHITE}  Estar MUY ACTIVO en estas horas:")
    for hour_data in top_hours:
        hour = int(hour_data['hour'])
        print(f"{Fore.CYAN}    • {hour:02d}:00 - {(hour+1):02d}:00 {Fore.WHITE}({hour_data['num_opportunities']} oportunidades)")
    print()

def display_daily_analysis(db: ArbitrageDatabaseAdvanced, fiat: str = "PEN", days: int = 30):
    """Análisis de mejores días para operar"""
    
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.GREEN}📅 ANÁLISIS: ¿QUÉ DÍAS SON MEJORES? - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*90}\n")
    
    daily = db.get_daily_profitability(fiat, days)
    
    if not daily:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    days_names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    
    best_day = max(daily, key=lambda x: x['num_opportunities'])
    
    print(f"{Fore.WHITE}{'Día':<15} {'Oportunidades':<15} {'Spread Prom':<15} {'Ganancia Total':<20}")
    print(f"{Fore.CYAN}{'-'*70}")
    
    for day_data in daily:
        day_num = int(day_data['day_of_week'])
        day_name = days_names[day_num]
        num_opps = day_data['num_opportunities']
        avg_spread = day_data['avg_spread']
        total_profit = day_data['total_potential_profit']
        
        if day_num == int(best_day['day_of_week']):
            color = Fore.GREEN
            icon = "🏆"
        elif num_opps >= best_day['num_opportunities'] * 0.7:
            color = Fore.YELLOW
            icon = "⭐"
        else:
            color = Fore.WHITE
            icon = "  "
        
        print(f"{color}{icon} {day_name:<13} {num_opps:<15} {avg_spread:.2f}%{' '*9} {total_profit:,.2f} {fiat}")
    
    print(f"\n{Fore.GREEN}💡 RECOMENDACIÓN:")
    best_day_name = days_names[int(best_day['day_of_week'])]
    print(f"{Fore.WHITE}  El mejor día es: {Fore.CYAN}{best_day_name} {Fore.WHITE}({best_day['num_opportunities']} oportunidades)")
    print()

def display_pair_recommendations(db: ArbitrageDatabaseAdvanced, fiat: str = "PEN", days: int = 7):
    """Mejores pares de exchanges para arbitrar"""
    
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.GREEN}🔄 ANÁLISIS: ¿ENTRE QUÉ EXCHANGES ARBITRAR? - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*90}\n")
    
    pairs = db.get_exchange_pair_performance(fiat, days, limit=10)
    
    if not pairs:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    for i, pair in enumerate(pairs, 1):
        if i <= 3:
            color = Fore.GREEN
            icon = "🔥"
        else:
            color = Fore.WHITE
            icon = "💡"
        
        print(f"{color}{icon} #{i} {pair['coin']}")
        print(f"   {Fore.CYAN}Comprar en:  {pair['buy_exchange']:<30}")
        print(f"   {Fore.MAGENTA}Vender en:   {pair['sell_exchange']:<30}")
        print(f"   {Fore.WHITE}Frecuencia: {pair['frequency']} veces | "
              f"Spread prom: {pair['avg_spread']:.2f}% | "
              f"Ganancia total: {pair['total_potential_profit']:,.2f} {fiat}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Análisis Profesional de Arbitraje - Optimizado para PEN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python arbitrage_pro_analysis.py --fiat PEN              # Análisis completo
  python arbitrage_pro_analysis.py --fiat PEN --days 30   # Últimos 30 días
  python arbitrage_pro_analysis.py --exchanges-only       # Solo recomendaciones de exchanges
        """
    )
    
    parser.add_argument('--fiat', type=str, default='PEN', help='Moneda fiat (default: PEN)')
    parser.add_argument('--days', type=int, default=7, help='Días a analizar (default: 7)')
    parser.add_argument('--db-path', type=str, default='arbitrage_advanced.db', help='Ruta a la BD')
    parser.add_argument('--exchanges-only', action='store_true', help='Solo exchanges')
    parser.add_argument('--hours-only', action='store_true', help='Solo horas')
    parser.add_argument('--days-only', action='store_true', help='Solo días')
    parser.add_argument('--pairs-only', action='store_true', help='Solo pares')
    
    args = parser.parse_args()
    
    try:
        db = ArbitrageDatabaseAdvanced(db_path=args.db_path)
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")
        print(f"{Fore.YELLOW}💡 Ejecuta el monitor con: --save-db --use-advanced-db")
        return
    
    total_snapshots = db.get_total_snapshots()
    total_opps = db.get_total_opportunities()
    
    if total_snapshots == 0:
        print(f"\n{Fore.YELLOW}⚠️  La base de datos está vacía")
        print(f"{Fore.CYAN}💡 Ejecuta el monitor con:")
        print(f"{Fore.WHITE}   python arbitrage/arbitrage_monitor.py --fiats {args.fiat} --save-db --use-advanced-db\n")
        db.close()
        return
    
    print(f"\n{Fore.GREEN}📊 Base de datos: {total_snapshots} snapshots | {total_opps} oportunidades")
    
    if args.exchanges_only:
        display_exchange_recommendations(db, args.fiat, args.days)
    elif args.hours_only:
        display_hourly_analysis(db, args.fiat, args.days)
    elif args.days_only:
        display_daily_analysis(db, args.fiat, min(args.days, 30))
    elif args.pairs_only:
        display_pair_recommendations(db, args.fiat, args.days)
    else:
        # Análisis completo
        display_exchange_recommendations(db, args.fiat, args.days)
        display_hourly_analysis(db, args.fiat, args.days)
        display_daily_analysis(db, args.fiat, min(args.days, 30))
        display_pair_recommendations(db, args.fiat, args.days)
    
    db.close()

if __name__ == "__main__":
    main()
