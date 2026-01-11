# 🚀 Guía de Deployment 24/7

## Opciones de Deployment (Gratis/Barato)

### **Opción 1: Railway.app (RECOMENDADA)** ⭐
- ✅ **Gratis**: $5 crédito mensual
- ✅ **PostgreSQL incluido** gratis
- ✅ **Muy fácil** de configurar
- ✅ **Deploy automático** desde GitHub

**Pasos:**
1. Crear cuenta en [railway.app](https://railway.app)
2. Crear nuevo proyecto → "Deploy from GitHub"
3. Conectar tu repositorio
4. Railway detecta Python automáticamente
5. Agregar PostgreSQL desde "New" → "Database" → "PostgreSQL"
6. ¡Listo! Corre 24/7

**Costo**: Gratis (hasta $5/mes de uso)

---

### **Opción 2: Render.com**
- ✅ **Gratis**: 750 horas/mes
- ✅ **PostgreSQL gratis** (90 días)
- ⚠️ Se duerme después de 15 min de inactividad

**Pasos:**
1. Crear cuenta en [render.com](https://render.com)
2. New → "Web Service"
3. Conectar GitHub
4. Configurar:
   - Build: `pip install -r requirements.txt`
   - Start: `python arbitrage_monitor.py --fiats PEN --save-db`
5. Agregar PostgreSQL desde "New" → "PostgreSQL"

**Costo**: Gratis

---

### **Opción 3: VPS (DigitalOcean/Vultr)**
- ✅ **Control total**
- ✅ **Siempre activo**
- ⚠️ Requiere configuración manual

**Costo**: $4-6/mes

---

## 📝 Archivos Necesarios

### 1. `Procfile` (para Railway/Render)
```
worker: python arbitrage_monitor.py --fiats PEN --save-db --interval 30
```

### 2. `runtime.txt` (opcional)
```
python-3.11
```

### 3. `.env` (variables de entorno)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 🔧 Configuración Paso a Paso (Railway)

### **Paso 1: Preparar el Código**

```bash
# En tu PC, crear estos archivos:

# Procfile
echo "worker: python arbitrage_monitor.py --fiats PEN --save-db" > Procfile

# .gitignore
echo "*.db
.env
__pycache__/" > .gitignore
```

### **Paso 2: Subir a GitHub**

```bash
git init
git add .
git commit -m "Arbitrage monitor ready for deployment"
git remote add origin https://github.com/tu-usuario/arbitrage-monitor.git
git push -u origin main
```

### **Paso 3: Deploy en Railway**

1. Ir a [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Seleccionar tu repositorio
4. Railway detecta Python y despliega automáticamente

### **Paso 4: Agregar PostgreSQL**

1. En tu proyecto Railway, click "New"
2. Seleccionar "Database" → "Add PostgreSQL"
3. Railway crea la variable `DATABASE_URL` automáticamente
4. Tu script la detecta y usa PostgreSQL

### **Paso 5: Verificar**

1. Ver logs en Railway
2. Deberías ver: `✓ Conectado a PostgreSQL`
3. El monitor corre 24/7

---

## 💾 Acceder a los Datos

### **Desde tu PC:**

```bash
# Instalar dependencias
pip install psycopg2-binary python-dotenv

# Crear .env con tu DATABASE_URL de Railway
echo "DATABASE_URL=postgresql://..." > .env

# Analizar datos
python arbitrage_analytics.py --fiat PEN
python arbitrage_time_analysis.py --fiat PEN
```

### **Desde cualquier lugar:**

Puedes conectarte a PostgreSQL con herramientas como:
- **pgAdmin** (GUI)
- **DBeaver** (GUI)
- **psql** (CLI)

---

## 📊 Arquitectura Final

```
┌─────────────────────────────────────┐
│  Railway/Render (Servidor 24/7)    │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ arbitrage_monitor.py          │ │
│  │ - Consulta API CriptoYa       │ │
│  │ - Detecta oportunidades       │ │
│  │ - Guarda en PostgreSQL        │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │ PostgreSQL Database           │ │
│  │ - Almacena oportunidades      │ │
│  │ - Accesible desde internet    │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Tu PC (cuando quieras analizar)   │
│                                     │
│  python arbitrage_analytics.py     │
│  python arbitrage_time_analysis.py │
└─────────────────────────────────────┘
```

---

## ✅ Ventajas de esta Arquitectura

1. ✅ **Monitor corre 24/7** sin tu PC
2. ✅ **Datos en la nube** (PostgreSQL)
3. ✅ **Acceso desde cualquier lugar**
4. ✅ **Gratis o muy barato** ($0-5/mes)
5. ✅ **Escalable** (puedes agregar más monedas)

---

## 🎯 Recomendación Final

**Para Perú (PEN):**

1. **Usar Railway.app** (más fácil y confiable)
2. **Configuración:**
   ```
   Monedas: USDT, BTC (las más líquidas)
   Fiat: PEN
   Intervalo: 30s
   Spread mínimo: 0.5%
   ```

3. **Dejar correr 2-4 semanas**

4. **Analizar desde tu PC** cuando quieras:
   ```bash
   python arbitrage_time_analysis.py --fiat PEN --days 30
   ```

5. **Tomar decisiones** basadas en datos reales

---

## 💰 Costos Estimados

| Opción | Costo Mensual | PostgreSQL | Uptime |
|--------|---------------|------------|--------|
| Railway | $0-5 | ✅ Incluido | 100% |
| Render | $0 | ✅ 90 días gratis | 100% |
| VPS | $4-6 | ⚠️ Debes instalar | 100% |

**Recomendación**: Empezar con **Railway** (gratis los primeros meses).

---

¿Quieres que te ayude a configurar el deployment en Railway paso a paso? 🚀
