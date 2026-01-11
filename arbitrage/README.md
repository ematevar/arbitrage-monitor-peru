# 📊 Sistema de Monitoreo de Arbitraje CriptoYa

Sistema completo para monitorear, analizar y aprovechar oportunidades de arbitraje de criptomonedas en Latinoamérica.

## 🚀 Inicio Rápido

### Instalación

```bash
pip install -r requirements.txt
```

### Uso Básico

```bash
# Monitor en tiempo real
python arbitrage/arbitrage_monitor.py --fiats PEN

# Con base de datos
python arbitrage/arbitrage_monitor.py --fiats PEN --save-db

# Análisis de datos
python arbitrage/arbitrage_analytics.py --fiat PEN
python arbitrage/arbitrage_time_analysis.py --fiat PEN
```

## 📁 Estructura del Proyecto

```
criptoya-api-docs/
├── arbitrage/                    # Sistema de arbitraje
│   ├── arbitrage_monitor.py      # Monitor principal
│   ├── arbitrage_analytics.py    # Análisis de exchanges
│   ├── arbitrage_time_analysis.py # Análisis temporal
│   ├── arbitrage_db.py           # Módulo de base de datos
│   ├── fee_analyzer.py           # Análisis de comisiones
│   └── docs/                     # Documentación
│       ├── README_ARBITRAGE.md   # Guía completa
│       └── DEPLOYMENT.md         # Guía de deployment
├── .vitepress/                   # Documentación API CriptoYa
├── Procfile                      # Configuración Railway
├── requirements.txt              # Dependencias Python
└── .env.example                  # Variables de entorno
```

## 📖 Documentación

- **[Guía de Arbitraje](arbitrage/docs/README_ARBITRAGE.md)** - Documentación completa del sistema
- **[Deployment 24/7](arbitrage/docs/DEPLOYMENT.md)** - Cómo deployar en Railway/Render

## 🎯 Características

- ✅ Monitoreo en tiempo real de spreads
- ✅ Base de datos SQLite/PostgreSQL
- ✅ Análisis temporal (mejores horas/días)
- ✅ Recomendaciones de distribución de fondos
- ✅ Análisis de comisiones por red
- ✅ Deploy 24/7 en la nube

## 💰 Países Soportados

ARS (Argentina), PEN (Perú), BRL (Brasil), CLP (Chile), COP (Colombia), MXN (México), USD, y más.

## 🚀 Deploy 24/7

Ver [DEPLOYMENT.md](arbitrage/docs/DEPLOYMENT.md) para instrucciones completas.

```bash
# Deploy en Railway
git push
# Railway despliega automáticamente
```

## 📊 Ejemplos de Uso

### Monitor Simple
```bash
python arbitrage/arbitrage_monitor.py --fiats PEN --spread 0.5
```

### Análisis Completo
```bash
# Recopilar datos por 1 semana
python arbitrage/arbitrage_monitor.py --fiats PEN --save-db

# Analizar patrones
python arbitrage/arbitrage_time_analysis.py --fiat PEN --days 7
```

## 🔧 Configuración

Ver `.env.example` para configurar PostgreSQL:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## 📝 Licencia

MIT

---

**Documentación API CriptoYa**: Ver carpetas por país (argentina/, peru/, etc.)
