# 📊 Monitor de Arbitraje CriptoYa

Script en Python para monitorear en tiempo real los mejores spreads y oportunidades de arbitraje entre diferentes exchanges usando la API de CriptoYa.

## 🚀 Características

- ✅ Monitoreo en tiempo real de múltiples criptomonedas y exchanges
- ✅ Cálculo automático de spreads y ganancias potenciales
- ✅ Actualización automática configurable
- ✅ Interfaz colorida en terminal con indicadores visuales
- ✅ Filtrado por spread mínimo
- ✅ Soporte para múltiples monedas fiat (ARS, USD, BRL, CLP, COP, MXN, PEN)
- ✅ Top de mejores oportunidades ordenadas por rentabilidad

## 📋 Requisitos

- Python 3.7 o superior
- Conexión a Internet

## 🔧 Instalación

1. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install requests colorama
```

## 💻 Uso

### Uso básico

Ejecutar con configuración por defecto (spread mínimo 0.5%, actualización cada 10 segundos):

```bash
python arbitrage_monitor.py
```

### Opciones avanzadas

**Configurar spread mínimo:**
```bash
python arbitrage_monitor.py --spread 1.0
```

**Configurar intervalo de actualización:**
```bash
python arbitrage_monitor.py --interval 5
```

**Monitorear criptomonedas específicas:**
```bash
python arbitrage_monitor.py --coins BTC ETH USDT
```

**Monitorear monedas fiat específicas:**
```bash
python arbitrage_monitor.py --fiats ARS USD
```

**Combinación de opciones:**
```bash
python arbitrage_monitor.py --spread 2 --interval 15 --coins BTC ETH --fiats ARS
```

### Ayuda

Ver todas las opciones disponibles:

```bash
python arbitrage_monitor.py --help
```

## 📊 Interpretación de Resultados

El script muestra las oportunidades de arbitraje con el siguiente formato:

```
🔥 #1 BTC/ARS
   Comprar en:  Binance P2P          @ 95,000.00 ARS
   Vender en:   Ripio                @ 98,500.00 ARS
   Spread: 3.68% | Ganancia: 3,500.00 ARS
```

### Indicadores visuales:

- 🔥 **Verde** - Spread >= 5% (Oportunidad excelente)
- ⭐ **Amarillo** - Spread >= 2% (Oportunidad buena)
- 💡 **Blanco** - Spread < 2% (Oportunidad moderada)

### Información mostrada:

- **Par de trading**: Criptomoneda/Fiat (ej: BTC/ARS)
- **Comprar en**: Exchange donde comprar al mejor precio
- **Vender en**: Exchange donde vender al mejor precio
- **Spread**: Diferencia porcentual entre compra y venta
- **Ganancia**: Ganancia potencial por unidad de criptomoneda

## ⚙️ Configuración

Puedes modificar las siguientes variables en el código para personalizar el comportamiento:

```python
# En la clase CriptoYaArbitrageMonitor:
COINS = ["BTC", "ETH", "USDT", "USDC", "DAI", "BNB", "SOL", "DOGE", "ADA", "MATIC"]
FIATS = ["ARS", "USD", "BRL", "CLP", "COP", "MXN", "PEN"]
VOLUME = 1.0  # Volumen para consultar
MIN_SPREAD_THRESHOLD = 0.5  # Spread mínimo en %
```

## 🎯 Criptomonedas Soportadas

BTC, ETH, USDT, USDC, DAI, UXD, USDP, WLD, BNB, SOL, XRP, ADA, AVAX, DOGE, TRX, LINK, DOT, MATIC, SHIB, LTC, BCH, EOS, XLM, FTM, AAVE, UNI, ALGO, BAT, PAXG, CAKE, AXS, SLP, MANA, SAND, CHZ

## 💱 Monedas Fiat Soportadas

- **ARS** - Peso Argentino
- **BRL** - Real Brasileño
- **CLP** - Peso Chileno
- **COP** - Peso Colombiano
- **MXN** - Peso Mexicano
- **PEN** - Sol Peruano
- **VES** - Bolívar Venezolano
- **BOB** - Boliviano
- **UYU** - Peso Uruguayo
- **DOP** - Peso Dominicano
- **PYG** - Guaraní Paraguayo
- **USD** - Dólar Estadounidense
- **EUR** - Euro

## ⚠️ Consideraciones Importantes

### ✅ Comisiones YA Incluidas

**IMPORTANTE**: La API de CriptoYa ya incluye todas las comisiones en los precios mostrados:

- **`totalAsk`** (precio de compra): Incluye comisiones de trading + comisiones de transferencia de red
- **`totalBid`** (precio de venta): Incluye comisiones de trading + comisiones de transferencia de red

Esto significa que **el spread calculado es la ganancia neta real** que obtendrías, ya considerando todos los costos.

### 🔍 Análisis de Comisiones por Red

Para ver las comisiones específicas de cada red de transferencia, usa el script `fee_analyzer.py`:

```bash
# Ver todas las comisiones
python fee_analyzer.py

# Ver comisiones de una criptomoneda específica
python fee_analyzer.py --coin USDT

# Ver comisiones de un exchange específico
python fee_analyzer.py --exchange "Binance P2P"

# Comparar comisiones de una red entre exchanges
python fee_analyzer.py --compare USDT TRON
```

### Otras Consideraciones

1. **Liquidez**: Asegúrate de que haya suficiente liquidez en ambos exchanges para ejecutar la operación.

3. **Tiempo de transferencia**: Considera el tiempo que toma transferir criptomonedas entre exchanges.

4. **Volatilidad**: Los precios pueden cambiar rápidamente, especialmente en mercados volátiles.

5. **Verificación**: Siempre verifica manualmente las oportunidades antes de ejecutar operaciones.

6. **Límites de API**: El script incluye pausas para no saturar la API de CriptoYa.

## 🔄 Flujo de Arbitraje

1. **Comprar** la criptomoneda en el exchange con el precio más bajo (`totalAsk`)
2. **Transferir** la criptomoneda al exchange con el precio más alto
3. **Vender** la criptomoneda en el exchange con el precio más alto (`totalBid`)
4. **Ganancia** = Precio de venta - Precio de compra

## 📝 Ejemplo de Salida

```
 📊 MONITOR DE ARBITRAJE CRIPTOYA 
Actualizado: 2026-01-11 10:15:30
Umbral mínimo de spread: 0.5%
Intervalo de actualización: 10s

 🚀 TOP 10 OPORTUNIDADES DE ARBITRAJE 

🔥 #1 USDT/ARS
   Comprar en:  Binance P2P          @ 1,050.00 ARS
   Vender en:   Ripio                @ 1,095.00 ARS
   Spread: 4.29% | Ganancia: 45.00 ARS

⭐ #2 BTC/ARS
   Comprar en:  Buenbit              @ 95,000.00 ARS
   Vender en:   Lemon                @ 97,500.00 ARS
   Spread: 2.63% | Ganancia: 2,500.00 ARS

💡 #3 ETH/USD
   Comprar en:  Binance              @ 3,200.00 USD
   Vender en:   Bitso                @ 3,235.00 USD
   Spread: 1.09% | Ganancia: 35.00 USD

────────────────────────────────────────────────────────────────────────────────
📈 Resumen: 15 oportunidades | Spread promedio: 1.85% | Spread máximo: 4.29%
────────────────────────────────────────────────────────────────────────────────
```

## 🛠️ Solución de Problemas

**Error de conexión:**
- Verifica tu conexión a Internet
- La API de CriptoYa puede estar temporalmente no disponible

**No se muestran oportunidades:**
- Reduce el umbral de spread mínimo con `--spread 0.1`
- Verifica que las monedas configuradas estén disponibles

**El script se ejecuta muy lento:**
- Reduce la cantidad de monedas a monitorear
- Aumenta el intervalo de actualización

## 📄 Licencia

Este script es de código abierto y puede ser usado libremente.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request en el repositorio.

## ⚖️ Disclaimer

Este script es solo para fines informativos y educativos. No constituye asesoramiento financiero. El trading de criptomonedas conlleva riesgos. Siempre realiza tu propia investigación antes de realizar operaciones.
