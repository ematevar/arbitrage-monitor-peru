# 🚀 Sistema de Monitoreo de Arbitraje CriptoYa

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema profesional para monitorear, analizar y aprovechar oportunidades de arbitraje de criptomonedas en Latinoamérica, optimizado para **Perú (PEN)**.

## ✨ Características

- 📊 **Monitoreo en tiempo real** de spreads entre exchanges
- 💾 **Base de datos avanzada** con PostgreSQL/SQLite
- 📈 **Análisis profesional** para optimizar distribución de fondos
- ⏰ **Análisis temporal** (mejores horas y días)
- 🚀 **Deploy 24/7** en Railway con PostgreSQL
- 🔍 **Análisis de comisiones** por red blockchain

## 🎯 ¿Qué Problemas Resuelve?

1. **¿En qué exchanges debo tener mis fondos?** → Análisis de rendimiento por exchange
2. **¿A qué horas debo estar activo?** → Análisis de rentabilidad por hora
3. **¿Qué días son mejores para arbitrar?** → Análisis de rentabilidad por día
4. **¿Entre qué exchanges arbitrar?** → Mejores pares de exchanges

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/criptoya-api-docs.git
cd criptoya-api-docs

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico

```bash
# Monitor en tiempo real
python arbitrage/arbitrage_monitor.py --fiats PEN

# Con base de datos avanzada
python arbitrage/arbitrage_monitor.py --fiats PEN --save-db --use-advanced-db

# Análisis profesional (después de recopilar datos)
python arbitrage/arbitrage_pro_analysis.py --fiat PEN
```

## 📁 Estructura del Proyecto

```
criptoya-api-docs/
├── arbitrage/                          # Sistema de arbitraje
│   ├── arbitrage_monitor.py            # Monitor principal
│   ├── arbitrage_db_advanced.py        # Base de datos avanzada
│   ├── arbitrage_pro_analysis.py       # Análisis profesional
│   ├── arbitrage_analytics.py          # Análisis de exchanges
│   ├── arbitrage_time_analysis.py      # Análisis temporal
│   ├── fee_analyzer.py                 # Análisis de comisiones
│   └── docs/                           # Documentación
│       ├── README_ARBITRAGE.md         # Guía completa
│       ├── DEPLOYMENT.md               # Guía de deployment
│       └── DATABASE_SCHEMA.md          # Esquema de BD
├── Procfile                            # Configuración Railway
├── requirements.txt                    # Dependencias Python
├── runtime.txt                         # Versión Python
└── railway.json                        # Configuración Railway
```

## 💻 Comandos Principales

### Monitoreo

```bash
# Monitor básico
python arbitrage/arbitrage_monitor.py --fiats PEN

# Con base de datos avanzada (recomendado)
python arbitrage/arbitrage_monitor.py --fiats PEN --save-db --use-advanced-db

# Personalizado
python arbitrage/arbitrage_monitor.py --fiats PEN USD --coins USDT BTC --spread 0.5
```

### Análisis

```bash
# Análisis completo
python arbitrage/arbitrage_pro_analysis.py --fiat PEN

# Solo exchanges (más importante)
python arbitrage/arbitrage_pro_analysis.py --fiat PEN --exchanges-only

# Solo horas
python arbitrage/arbitrage_pro_analysis.py --fiat PEN --hours-only

# Análisis de 30 días
python arbitrage/arbitrage_pro_analysis.py --fiat PEN --days 30
```

## 🌐 Deploy en Railway (24/7)

### Paso 1: Push a GitHub

```bash
git add .
git commit -m "Add arbitrage monitoring system"
git push origin main
```

### Paso 2: Deploy en Railway

1. Ir a [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Seleccionar tu repositorio
4. **Add PostgreSQL** desde el menú "New"
5. ¡Listo! Corre 24/7

Ver [DEPLOYMENT.md](arbitrage/docs/DEPLOYMENT.md) para guía completa.

## 📊 Ejemplo de Análisis

```
💰 RECOMENDACIÓN: ¿EN QUÉ EXCHANGES METER MIS FONDOS? - PEN

Exchange                  Compras    Ventas     Total      Ganancia Potencial
----------------------------------------------------------------------------------
🥇 Binance P2P           85         65         150        1,250.50 PEN
🥈 Bitso                 70         75         145        1,180.30 PEN
🥉 Buda                  45         50         95         850.20 PEN

💡 RECOMENDACIÓN DE DISTRIBUCIÓN:
  1. Binance P2P    → 40.5% de tus fondos
  2. Bitso          → 39.2% de tus fondos
  3. Buda           → 20.3% de tus fondos
```

## 🔧 Configuración

### Variables de Entorno

```bash
# .env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Opciones del Monitor

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--fiats` | Monedas fiat a monitorear | ARS, USD |
| `--coins` | Criptomonedas a monitorear | BTC, ETH, USDT, USDC |
| `--spread` | Spread mínimo (%) | 0.5 |
| `--interval` | Intervalo de actualización (s) | 30 |
| `--save-db` | Guardar en base de datos | False |
| `--use-advanced-db` | Usar esquema avanzado | False |

## 📚 Documentación

- [Guía Completa de Arbitraje](arbitrage/docs/README_ARBITRAGE.md)
- [Guía de Deployment](arbitrage/docs/DEPLOYMENT.md)
- [Esquema de Base de Datos](arbitrage/docs/DATABASE_SCHEMA.md)

## 🌍 Países Soportados

ARS (Argentina), **PEN (Perú)**, BRL (Brasil), CLP (Chile), COP (Colombia), MXN (México), USD, EUR

## 💰 Costos

- **Railway**: Gratis (primeros meses) → $5/mes
- **PostgreSQL**: Incluido gratis
- **Total**: $0 → $5/mes

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles

## 🙏 Agradecimientos

- [CriptoYa API](https://criptoya.com/api) por proporcionar datos en tiempo real
- Comunidad de arbitraje de criptomonedas

## 📧 Contacto

Para preguntas o soporte, abre un issue en GitHub.

---

**⚠️ Disclaimer**: Este software es solo para fines educativos. El arbitraje de criptomonedas conlleva riesgos. Investiga y comprende los riesgos antes de operar.
