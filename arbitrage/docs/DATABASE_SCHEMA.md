# 📊 Esquema de Base de Datos Mejorado

## Esquema Actual (Básico)

```sql
opportunities (
    id,
    timestamp,
    coin,
    fiat,
    buy_exchange,
    sell_exchange,
    buy_price,      -- Solo precio final
    sell_price,     -- Solo precio final
    spread_percentage,
    profit_per_unit
)
```

**Limitaciones:**
- ❌ No guarda precios sin comisiones (ask/bid raw)
- ❌ No guarda datos de TODOS los exchanges (solo los 2 mejores)
- ❌ No guarda volumen consultado
- ❌ No guarda metadata de la API
- ❌ Difícil analizar volatilidad
- ❌ No permite reconstruir el mercado completo

---

## Esquema Mejorado (Detallado)

### **Tabla 1: `market_snapshots`** (Foto completa del mercado)
```sql
market_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    coin VARCHAR(20) NOT NULL,
    fiat VARCHAR(10) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    snapshot_hash VARCHAR(64),  -- Hash único del snapshot
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### **Tabla 2: `exchange_quotes`** (Cotización de cada exchange)
```sql
exchange_quotes (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER REFERENCES market_snapshots(id),
    exchange VARCHAR(100) NOT NULL,
    
    -- Precios sin comisiones
    ask DECIMAL(20, 8),              -- Precio compra sin comisiones
    bid DECIMAL(20, 8),              -- Precio venta sin comisiones
    
    -- Precios con comisiones (finales)
    total_ask DECIMAL(20, 8),        -- Precio compra CON comisiones
    total_bid DECIMAL(20, 8),        -- Precio venta CON comisiones
    
    -- Metadata
    api_timestamp INTEGER,           -- Timestamp de la API
    response_time_ms INTEGER,        -- Tiempo de respuesta
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### **Tabla 3: `arbitrage_opportunities`** (Oportunidades detectadas)
```sql
arbitrage_opportunities (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER REFERENCES market_snapshots(id),
    
    -- Exchanges involucrados
    buy_exchange_quote_id INTEGER REFERENCES exchange_quotes(id),
    sell_exchange_quote_id INTEGER REFERENCES exchange_quotes(id),
    
    -- Cálculos
    spread_percentage DECIMAL(10, 4) NOT NULL,
    profit_per_unit DECIMAL(20, 8) NOT NULL,
    profit_percentage DECIMAL(10, 4),
    
    -- Metadata
    execution_feasibility VARCHAR(20),  -- 'high', 'medium', 'low'
    estimated_execution_time_minutes INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### **Tabla 4: `exchange_metadata`** (Info de exchanges)
```sql
exchange_metadata (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    type VARCHAR(50),  -- 'P2P', 'Spot', 'DEX'
    supports_instant_transfer BOOLEAN,
    average_deposit_time_minutes INTEGER,
    average_withdrawal_time_minutes INTEGER,
    last_updated TIMESTAMP
)
```

---

## Ventajas del Nuevo Esquema

### ✅ **Análisis Completo del Mercado**
```sql
-- Ver TODOS los exchanges en un momento específico
SELECT * FROM exchange_quotes WHERE snapshot_id = 123;
```

### ✅ **Análisis de Volatilidad**
```sql
-- Ver cómo cambian los precios en el tiempo
SELECT timestamp, exchange, total_ask, total_bid
FROM market_snapshots ms
JOIN exchange_quotes eq ON ms.id = eq.snapshot_id
WHERE coin = 'USDT' AND fiat = 'PEN'
ORDER BY timestamp;
```

### ✅ **Análisis de Comisiones**
```sql
-- Comparar precios con/sin comisiones
SELECT 
    exchange,
    ask,
    total_ask,
    (total_ask - ask) as commission_amount,
    ((total_ask - ask) / ask * 100) as commission_percentage
FROM exchange_quotes;
```

### ✅ **Análisis de Spreads Internos**
```sql
-- Ver spread dentro del mismo exchange
SELECT 
    exchange,
    (total_ask - total_bid) as internal_spread,
    ((total_ask - total_bid) / total_bid * 100) as internal_spread_pct
FROM exchange_quotes;
```

### ✅ **Reconstrucción Histórica**
```sql
-- Reconstruir el mercado completo de hace 1 semana
SELECT * FROM market_snapshots ms
JOIN exchange_quotes eq ON ms.id = eq.snapshot_id
WHERE timestamp BETWEEN '2026-01-04' AND '2026-01-05';
```

### ✅ **Análisis de Rendimiento de API**
```sql
-- Ver qué exchanges responden más rápido
SELECT exchange, AVG(response_time_ms) as avg_response
FROM exchange_quotes
GROUP BY exchange
ORDER BY avg_response;
```

---

## Comparación de Tamaño

| Esquema | Registros/Hora | Tamaño/Día | Tamaño/Mes |
|---------|----------------|------------|------------|
| **Básico** | ~10 | ~240 KB | ~7 MB |
| **Detallado** | ~120 | ~2.8 MB | ~84 MB |

**Conclusión**: El esquema detallado usa ~12x más espacio pero da **100x más información**.

---

## Implementación Recomendada

### **Opción 1: Esquema Híbrido** (Recomendado)
- Guardar **snapshots completos** cada 5 minutos
- Guardar **solo oportunidades** en tiempo real

### **Opción 2: Solo Detallado**
- Guardar TODO siempre
- Más espacio pero análisis ilimitados

### **Opción 3: Mantener Básico**
- Más ligero
- Análisis limitados

---

¿Quieres que implemente el **esquema detallado**? Te permitirá:
- 📊 Análisis de volatilidad
- 💹 Comparación de comisiones
- 🔍 Reconstrucción histórica del mercado
- ⚡ Análisis de velocidad de exchanges
- 📈 Machine Learning futuro
