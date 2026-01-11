#!/usr/bin/env python3
"""
Análisis Temporal de Oportunidades de Arbitraje
Identifica las mejores horas y días para arbitrar
"""

import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from colorama import init, Fore, Style
from arbitrage_db import ArbitrageDatabase

# Inicializar colorama
init(autoreset=True)

def analyze_by_hour(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Analiza oportunidades por hora del día"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}⏰ ANÁLISIS POR HORA DEL DÍA - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    since_date = datetime.now() - timedelta(days=days)
    
    # Obtener todas las oportunidades
    cursor = db.conn.cursor()
    results = cursor.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as count,
            AVG(spread_percentage) as avg_spread,
            MAX(spread_percentage) as max_spread,
            AVG(profit_per_unit) as avg_profit
        FROM opportunities
        WHERE fiat = ? AND timestamp >= ?
        GROUP BY hour
        ORDER BY hour
    """, (fiat, since_date)).fetchall()
    
    if not results:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    # Convertir a diccionario
    hourly_data = {int(row['hour']): dict(row) for row in results}
    
    # Encontrar mejor hora
    best_hour = max(hourly_data.items(), key=lambda x: x[1]['count'])
    best_spread_hour = max(hourly_data.items(), key=lambda x: x[1]['avg_spread'])
    
    print(f"{Fore.WHITE}{'Hora':<10} {'Oportunidades':<15} {'Spread Prom':<15} {'Spread Máx':<15}")
    print(f"{Fore.CYAN}{'-'*60}")
    
    for hour in range(24):
        if hour in hourly_data:
            data = hourly_data[hour]
            
            # Colorear según cantidad de oportunidades
            if data['count'] >= best_hour[1]['count'] * 0.8:
                color = Fore.GREEN
                icon = "🔥"
            elif data['count'] >= best_hour[1]['count'] * 0.5:
                color = Fore.YELLOW
                icon = "⭐"
            else:
                color = Fore.WHITE
                icon = "  "
            
            hour_str = f"{hour:02d}:00"
            print(f"{color}{icon} {hour_str:<8} {data['count']:<15} "
                  f"{data['avg_spread']:.2f}%{' '*9} {data['max_spread']:.2f}%")
        else:
            print(f"{Fore.LIGHTBLACK_EX}   {hour:02d}:00    0               -               -")
    
    print(f"\n{Fore.GREEN}📊 RESUMEN:")
    print(f"{Fore.WHITE}🏆 Mejor hora (más oportunidades): {Fore.GREEN}{best_hour[0]:02d}:00 "
          f"{Fore.WHITE}con {Fore.CYAN}{best_hour[1]['count']} oportunidades")
    print(f"{Fore.WHITE}💰 Mejor hora (spread promedio): {Fore.GREEN}{best_spread_hour[0]:02d}:00 "
          f"{Fore.WHITE}con {Fore.CYAN}{best_spread_hour[1]['avg_spread']:.2f}% spread")
    print()

def analyze_by_day_of_week(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 30):
    """Analiza oportunidades por día de la semana"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}📅 ANÁLISIS POR DÍA DE LA SEMANA - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    since_date = datetime.now() - timedelta(days=days)
    
    cursor = db.conn.cursor()
    results = cursor.execute("""
        SELECT 
            CAST(strftime('%w', timestamp) AS INTEGER) as day_of_week,
            COUNT(*) as count,
            AVG(spread_percentage) as avg_spread,
            MAX(spread_percentage) as max_spread
        FROM opportunities
        WHERE fiat = ? AND timestamp >= ?
        GROUP BY day_of_week
        ORDER BY day_of_week
    """, (fiat, since_date)).fetchall()
    
    if not results:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    days_names = {
        0: "Domingo",
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado"
    }
    
    # Convertir a diccionario
    daily_data = {int(row['day_of_week']): dict(row) for row in results}
    
    # Encontrar mejor día
    best_day = max(daily_data.items(), key=lambda x: x[1]['count'])
    
    print(f"{Fore.WHITE}{'Día':<15} {'Oportunidades':<15} {'Spread Prom':<15} {'Spread Máx':<15}")
    print(f"{Fore.CYAN}{'-'*65}")
    
    for day_num in range(7):
        if day_num in daily_data:
            data = daily_data[day_num]
            
            if day_num == best_day[0]:
                color = Fore.GREEN
                icon = "🏆"
            elif data['count'] >= best_day[1]['count'] * 0.7:
                color = Fore.YELLOW
                icon = "⭐"
            else:
                color = Fore.WHITE
                icon = "  "
            
            print(f"{color}{icon} {days_names[day_num]:<13} {data['count']:<15} "
                  f"{data['avg_spread']:.2f}%{' '*9} {data['max_spread']:.2f}%")
        else:
            print(f"{Fore.LIGHTBLACK_EX}   {days_names[day_num]:<13} 0               -               -")
    
    print(f"\n{Fore.GREEN}📊 RESUMEN:")
    print(f"{Fore.WHITE}🏆 Mejor día: {Fore.GREEN}{days_names[best_day[0]]} "
          f"{Fore.WHITE}con {Fore.CYAN}{best_day[1]['count']} oportunidades")
    print()

def analyze_by_time_ranges(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Analiza oportunidades por rangos de tiempo del día"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}🕐 ANÁLISIS POR RANGO HORARIO - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    since_date = datetime.now() - timedelta(days=days)
    
    cursor = db.conn.cursor()
    results = cursor.execute("""
        SELECT 
            CASE 
                WHEN CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 0 AND 5 THEN 'Madrugada (00:00-05:59)'
                WHEN CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 6 AND 11 THEN 'Mañana (06:00-11:59)'
                WHEN CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 12 AND 17 THEN 'Tarde (12:00-17:59)'
                ELSE 'Noche (18:00-23:59)'
            END as time_range,
            COUNT(*) as count,
            AVG(spread_percentage) as avg_spread,
            MAX(spread_percentage) as max_spread
        FROM opportunities
        WHERE fiat = ? AND timestamp >= ?
        GROUP BY time_range
        ORDER BY 
            CASE time_range
                WHEN 'Madrugada (00:00-05:59)' THEN 1
                WHEN 'Mañana (06:00-11:59)' THEN 2
                WHEN 'Tarde (12:00-17:59)' THEN 3
                ELSE 4
            END
    """, (fiat, since_date)).fetchall()
    
    if not results:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    print(f"{Fore.WHITE}{'Rango Horario':<25} {'Oportunidades':<15} {'Spread Prom':<15}")
    print(f"{Fore.CYAN}{'-'*60}")
    
    for row in results:
        count = row['count']
        avg_spread = row['avg_spread']
        
        # Determinar color según cantidad
        if count >= 50:
            color = Fore.GREEN
            icon = "🔥"
        elif count >= 20:
            color = Fore.YELLOW
            icon = "⭐"
        else:
            color = Fore.WHITE
            icon = "💡"
        
        print(f"{color}{icon} {row['time_range']:<23} {count:<15} {avg_spread:.2f}%")
    
    print()

def analyze_hourly_heatmap(db: ArbitrageDatabase, fiat: str = "PEN", days: int = 7):
    """Crea un mapa de calor de oportunidades por hora y día"""
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.GREEN}🗓️  MAPA DE CALOR: HORA × DÍA - {fiat}")
    print(f"{Fore.CYAN}Últimos {days} días")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    since_date = datetime.now() - timedelta(days=days)
    
    cursor = db.conn.cursor()
    results = cursor.execute("""
        SELECT 
            CAST(strftime('%w', timestamp) AS INTEGER) as day_of_week,
            CAST(strftime('%H', timestamp) AS INTEGER) as hour,
            COUNT(*) as count
        FROM opportunities
        WHERE fiat = ? AND timestamp >= ?
        GROUP BY day_of_week, hour
    """, (fiat, since_date)).fetchall()
    
    if not results:
        print(f"{Fore.YELLOW}⚠️  No hay datos suficientes\n")
        return
    
    # Crear matriz
    heatmap = defaultdict(lambda: defaultdict(int))
    max_count = 0
    
    for row in results:
        day = row['day_of_week']
        hour = row['hour']
        count = row['count']
        heatmap[day][hour] = count
        max_count = max(max_count, count)
    
    days_abbr = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    
    # Encabezado
    print(f"{Fore.WHITE}     ", end="")
    for hour in range(0, 24, 3):
        print(f"{hour:02d}h  ", end="")
    print()
    
    # Filas por día
    for day in range(7):
        print(f"{Fore.CYAN}{days_abbr[day]} ", end="")
        
        for hour in range(0, 24, 3):
            count = heatmap[day][hour]
            
            if count == 0:
                symbol = "·"
                color = Fore.LIGHTBLACK_EX
            elif count >= max_count * 0.7:
                symbol = "█"
                color = Fore.GREEN
            elif count >= max_count * 0.4:
                symbol = "▓"
                color = Fore.YELLOW
            elif count >= max_count * 0.2:
                symbol = "▒"
                color = Fore.WHITE
            else:
                symbol = "░"
                color = Fore.LIGHTBLACK_EX
            
            print(f"{color}{symbol}    ", end="")
        print()
    
    print(f"\n{Fore.WHITE}Leyenda: {Fore.LIGHTBLACK_EX}· = 0  {Fore.WHITE}░ = Bajo  "
          f"{Fore.YELLOW}▒ = Medio  {Fore.YELLOW}▓ = Alto  {Fore.GREEN}█ = Muy Alto")
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Análisis Temporal de Oportunidades de Arbitraje',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python arbitrage_time_analysis.py --fiat PEN              # Análisis completo
  python arbitrage_time_analysis.py --fiat PEN --days 30   # Últimos 30 días
  python arbitrage_time_analysis.py --hours-only           # Solo análisis por hora
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
        '--hours-only',
        action='store_true',
        help='Mostrar solo análisis por hora'
    )
    
    parser.add_argument(
        '--days-only',
        action='store_true',
        help='Mostrar solo análisis por día de la semana'
    )
    
    parser.add_argument(
        '--heatmap-only',
        action='store_true',
        help='Mostrar solo mapa de calor'
    )
    
    args = parser.parse_args()
    
    # Abrir base de datos
    try:
        db = ArbitrageDatabase(args.db_path)
    except Exception as e:
        print(f"{Fore.RED}❌ Error al abrir base de datos: {e}")
        print(f"{Fore.YELLOW}💡 Ejecuta el monitor con --save-db primero")
        return
    
    total = db.get_total_opportunities()
    
    if total == 0:
        print(f"\n{Fore.YELLOW}⚠️  La base de datos está vacía")
        print(f"{Fore.CYAN}💡 Ejecuta el monitor con --save-db para recopilar datos\n")
        db.close()
        return
    
    print(f"\n{Fore.GREEN}📊 Base de datos: {total} oportunidades registradas")
    
    # Mostrar análisis según flags
    if args.hours_only:
        analyze_by_hour(db, args.fiat, args.days)
    elif args.days_only:
        analyze_by_day_of_week(db, args.fiat, args.days)
    elif args.heatmap_only:
        analyze_hourly_heatmap(db, args.fiat, args.days)
    else:
        # Mostrar todo
        analyze_by_hour(db, args.fiat, args.days)
        analyze_by_day_of_week(db, args.fiat, min(args.days, 30))
        analyze_by_time_ranges(db, args.fiat, args.days)
        analyze_hourly_heatmap(db, args.fiat, args.days)
    
    db.close()

if __name__ == "__main__":
    main()
