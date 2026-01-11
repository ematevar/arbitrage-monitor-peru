# 🚀 Sistema de Monitoreo de Arbitraje CriptoYa

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet)](https://railway.app)

Sistema profesional para monitorear, analizar y aprovechar oportunidades de arbitraje de criptomonedas en Latinoamérica, **optimizado para Perú (PEN)**.

## ✨ Características

- 📊 **Monitoreo 24/7** de spreads entre exchanges
- 💾 **Base de datos PostgreSQL** en la nube
- 📈 **Análisis profesional** para optimizar distribución de fondos
- ⏰ **Análisis temporal** (mejores horas y días)
- 🚀 **Deploy automático** en Railway
- 🔍 **Análisis de comisiones** incluidas en precios

## 🎯 ¿Qué Problemas Resuelve?

| Pregunta | Respuesta |
|----------|-----------|
| ¿En qué exchanges debo tener fondos? | Análisis de rendimiento histórico |
| ¿A qué horas estar activo? | Análisis de rentabilidad por hora |
| ¿Qué días son mejores? | Análisis de rentabilidad por día |
| ¿Entre qué exchanges arbitrar? | Mejores pares históricos |

## 🚀 Inicio Rápido

### Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/ematevar/arbitrage-monitor-peru.git
cd arbitrage-monitor-peru

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar monitor
python arbitrage/arbitrage_monitor.py --fiats PEN
```

### Deploy en Railway (Recomendado)

1. Fork este repositorio
2. Ir a [railway.app](https://railway.app)
3. **New Project** → **Deploy from GitHub repo**
4. Seleccionar tu fork
5. **Add PostgreSQL** (Click "New" → "Database" → "PostgreSQL")
6. ¡Listo! Corre 24/7 automáticamente

## 📁 Estructura del Proyecto

```
arbitrage-monitor-peru/
├── arbitrage/                      # Sistema de arbitraje
│   ├── arbitrage_monitor.py        # Monitor principal ⭐
│   ├── arbitrage_db_advanced.py    # Base de datos avanzada
│   ├── arbitrage_pro_analysis.py   # Análisis profesional
│   └── docs/                       # Documentación detallada
├── view_data.py                    # Ver datos de PostgreSQL ⭐
├── verify_postgres.py              # Verificar conexión
├── init_database.py                # Inicializar BD
├── Procfile                        # Configuración Railway
├── requirements.txt                # Dependencias
└── README.md                       # Este archivo
```

## 💻 Comandos Principales

### Monitoreo

```bash
# Monitor básico (local)
python arbitrage/arbitrage_monitor.py --fiats PEN

# Con base de datos avanzada (Railway)
python arbitrage/arbitrage_monitor.py --fiats PEN --save-db --use-advanced-db
```

### Análisis de Datos

```bash
# Ver datos actuales
python view_data.py

# Verificar conexión PostgreSQL
python verify_postgres.py

# Análisis completo (requiere 1-2 semanas de datos)
python arbitrage/arbitrage_pro_analysis.py --fiat PEN
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env`:

```bash
# Obtener de Railway → PostgreSQL → Connect
DATABASE_URL=postgresql://postgres:PASSWORD@host:port/railway
```

### Opciones del Monitor

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--fiats` | Monedas fiat | ARS, USD |
| `--coins` | Criptomonedas | BTC, ETH, USDT, USDC |
| `--spread` | Spread mínimo (%) | 0.5 |
| `--interval` | Intervalo (segundos) | 30 |
| `--save-db` | Guardar en BD | False |
| `--use-advanced-db` | Esquema avanzado | False |

## 📊 Ejemplo de Análisis

Después de 1-2 semanas de datos:

```
💰 DISTRIBUCIÓN RECOMENDADA:
  1. Satoshitango    → 45% de fondos
  2. Lemoncash       → 35% de fondos
  3. Binance P2P     → 20% de fondos

⏰ MEJORES HORAS:
  • 08:00-09:00 (85 oportunidades)
  • 14:00-15:00 (72 oportunidades)

📅 MEJOR DÍA:
  Lunes (120 oportunidades)
```

## 🌐 Deploy en Railway

### Paso 1: Configuración Inicial

1. Fork este repositorio
2. Crear cuenta en [Railway](https://railway.app)
3. Conectar con GitHub

### Paso 2: Deploy

1. **New Project** → **Deploy from GitHub repo**
2. Seleccionar `arbitrage-monitor-peru`
3. Railway detecta Python automáticamente
4. **Add PostgreSQL**: Click "New" → "Database" → "PostgreSQL"

### Paso 3: Verificación

Ver logs: Deployments → View Logs

Deberías ver:
```
✓ Conectado a PostgreSQL (Esquema Avanzado)
🚀 Iniciando Monitor de Arbitraje CriptoYa...
```

## 📚 Documentación Completa

- [Guía de Arbitraje](arbitrage/docs/README_ARBITRAGE.md) - Documentación completa
- [Esquema de Base de Datos](arbitrage/docs/DATABASE_SCHEMA.md) - Estructura de datos
- [Guía de Deployment](arbitrage/docs/DEPLOYMENT.md) - Deploy detallado

## 🌍 Países Soportados

ARS (Argentina), **PEN (Perú)**, BRL (Brasil), CLP (Chile), COP (Colombia), MXN (México), USD, EUR

## 💰 Costos

| Servicio | Costo |
|----------|-------|
| Railway (primeros meses) | **Gratis** |
| PostgreSQL | **Gratis** (incluido) |
| Después de crédito | **$5/mes** |

## 🛠️ Scripts Útiles

### `view_data.py`
Ver datos guardados en PostgreSQL:
- Total de snapshots y oportunidades
- Últimas oportunidades detectadas
- Top exchanges para comprar/vender

### `verify_postgres.py`
Verificar conexión a PostgreSQL desde tu PC

### `init_database.py`
Inicializar base de datos en Railway (si es necesario)

## 📈 Flujo de Trabajo Recomendado

1. **Semana 1-2**: Deploy en Railway, recopilación de datos
2. **Semana 3**: Primer análisis con `view_data.py`
3. **Semana 4**: Análisis completo, distribución de fondos
4. **Semana 5+**: Arbitraje optimizado en horas/días específicos

## ⚠️ Notas Importantes

- ✅ Los precios **YA INCLUYEN** todas las comisiones (trading + red)
- ⏱️ Las oportunidades duran **segundos**, pre-posiciona fondos
- 📊 Necesitas **1-2 semanas** de datos para análisis completos
- 🔒 Nunca subas tu `.env` a GitHub (ya está en `.gitignore`)

## 🤝 Contribuir

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE)

## 🙏 Agradecimientos

- [CriptoYa API](https://criptoya.com/api) - Datos en tiempo real
- [Railway](https://railway.app) - Hosting gratuito
- Comunidad de arbitraje de criptomonedas

## 📧 Soporte

Para preguntas o issues, abre un [issue en GitHub](https://github.com/ematevar/arbitrage-monitor-peru/issues).

---

**⚠️ Disclaimer**: Este software es solo para fines educativos. El arbitraje de criptomonedas conlleva riesgos. Investiga y comprende los riesgos antes de operar.

**Hecho con ❤️ en Perú 🇵🇪**
