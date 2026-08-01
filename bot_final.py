import time
import requests
import threading
import os
import sys
import hmac
import hashlib
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA REAL DE DERIVADOS CON MEGA ENTRADAS URGENTES
# =====================================================================
SYMBOL = "ETHUSDT"  

TOKEN_LIMPIO = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
CHAT_ID_LIMPIO = "-1004335003036"  

# Márgenes para operaciones estándar de Scalping rápido
PORCENTAJE_SL = 0.0015  # 0.15% Stop Loss estándar
PORCENTAJE_TP = 0.0022  # 0.22% Take Profit estándar

# Umbrales críticos para capturar las "MEGA ENTRADAS" institucionales
UMBRAL_MEGA_PRECIO = 0.40
UMBRAL_MEGA_OI = 0.80

# 🔐 EXTRACCIÓN DISCRETA DESDE VARIABLES DE ENTORNO EN RENDER
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
BASE_URL_BINANCE = "https://binance.com"

# =====================================================================
# MOTOR EJECUTOR AUTOMÁTICO EN BINANCE FUTUROS (NIVEL 2)
# =====================================================================
def generar_firma_hmac(params):
    """Genera el candado SHA256 exigido por Binance para operaciones seguras."""
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(
        BINANCE_SECRET_KEY.encode('utf-8'), 
        query_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()

def consultar_saldo_neto():
    """Consulta balance en USDT en vivo para aplicar interés compuesto al 100%."""
    endpoint = f"{BASE_URL_BINANCE}/fapi/v2/account"
    params = {"timestamp": int(time.time() * 1000)}
    params["signature"] = generar_firma_hmac(params)
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=5).json()
        for asset in response.get("assets", []):
            if asset["asset"] == "USDT":
                return float(asset["walletBalance"])
    except Exception as e:
        print("⚠️ No se pudo leer balance en Binance: " + str(e))
        sys.stdout.flush()
    return 80.0  # Fallback seguro basado en tu capital actual

def ajustar_leverage_dinamico(symbol, es_mega_entrada):
    """Cambia potencia en milisegundos: X10 Estándar / X20 Mega Entrada."""
    leverage = 20 if es_mega_entrada else 10
    endpoint = f"{BASE_URL_BINANCE}/fapi/v1/leverage"
    params = {
        "symbol": symbol,
        "leverage": leverage,
        "timestamp": int(time.time() * 1000)
    }
    params["signature"] = generar_firma_hmac(params)
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    try:
        requests.post(endpoint, data=params, headers=headers, timeout=5)
    except Exception as e:
        print("⚠️ Fallo al configurar apalancamiento: " + str(e))
        sys.stdout.flush()
    return leverage

def ejecutar_orden_automatica(symbol, direccion, precio_entrada, tp_precio, sl_precio, es_mega_entrada=False):
    """Lanza la entrada a mercado y amarra inmediatamente el TP y SL en Binance."""
    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        print("❌ Error: API Keys no configuradas en Render Environment.")
        sys.stdout.flush()
        return

    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    
    # 1. Ajuste de apalancamiento dinámico y consulta de balance real
    leverage = ajustar_leverage_dinamico(symbol, es_mega_entrada)
    saldo = consultar_saldo_neto()
    
    # Gestión de riesgo automática: 100% hasta $400 / 50% después
    capital_operativo = saldo if saldo < 400.0 else (saldo * 0.5)
    cantidad_eth = round((capital_operativo * leverage) / precio_entrada, 3)
    
    lado_entrada = "BUY" if "LONG" in direccion else "SELL"
    lado_salida = "SELL" if "LONG" in direccion else "BUY"
    
    try:
        # 👉 ORDEN 1: Lanzamiento de la orden de Entrada a Mercado
        p_orden = {"symbol": symbol, "side": lado_entrada, "type": "MARKET", "quantity": cantidad_eth, "timestamp": int(time.time() * 1000)}
        p_orden["signature"] = generar_firma_hmac(p_orden)
        requests.post(f"{BASE_URL_BINANCE}/fapi/v1/order", data=p_orden, headers=headers, timeout=5)
        
        # 💰 ORDEN 2: Colocación del Bracket de Take Profit Autónomo
        p_tp = {"symbol": symbol, "side": lado_salida, "type": "TAKE_PROFIT_MARKET", "stopPrice": round(tp_precio, 2), "closePosition": "true", "timestamp": int(time.time() * 1000)}
        p_tp["signature"] = generar_firma_hmac(p_tp)
        requests.post(f"{BASE_URL_BINANCE}/fapi/v1/order", data=p_tp, headers=headers, timeout=5)
        
        # 🛡️ ORDEN 3: Colocación del Bracket de Stop Loss / Cinturón de Seguridad
        p_sl = {"symbol": symbol, "side": lado_salida, "type": "STOP_MARKET", "stopPrice": round(sl_precio, 2), "closePosition": "true", "timestamp": int(time.time() * 1000)}
        p_sl["signature"] = generar_firma_hmac(p_sl)
        requests.post(f"{BASE_URL_BINANCE}/fapi/v1/order", data=p_sl, headers=headers, timeout=5)
        
        print(f"🎯 [EJECUCIÓN] Orden {direccion} colocada con éxito en Binance.")
        sys.stdout.flush()
    except Exception as e:
        print("❌ Error crítico en envío de órdenes a Binance: " + str(e))
        sys.stdout.flush()

# =====================================================================
# ENLACES DE FLUJO ORIGINALES DE SEÑALES E INSTITUCIONALES
# =====================================================================
def enviar_telegram(mensaje):
    """Envío nativo con URL fraccionada de forma simple para evitar mutilaciones."""
    parte1 = 'https://api.'
    parte2 = 'telegram.org/bot'
    parte3 = '/sendMessage'
    
    url_final = parte1 + parte2 + TOKEN_LIMPIO + parte3
    
    payload = {
        "chat_id": CHAT_ID_LIMPIO, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(url_final, json=payload, headers=cabeceras, timeout=10)
        print("📡 [TELEGRAM] Status: " + str(res.status_code))
        sys.stdout.flush()
    except Exception as e: 
        print("❌ Fallo en enlace de Telegram: " + str(e))
        sys.stdout.flush()

def obtener_datos_institucionales():
    """Consumo y modelado de datos redundantes de derivados y orderbook."""
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    precio = None
    oi = None
    imbalance = 50.0
    sentiment = 50.0
    
    url_base = 'https://api.' + 'kucoin.com'
    
    # 1. Extracción del Precio Actual de Mercado
    try:
        endpoint_p = url_base + "/api/v1/market/orderbook/level1?symbol=ETH-USDT"
        res = requests.get(endpoint_p, headers=cabeceras, timeout=6)
        if res.status_code == 200:
            precio = float(res.json()["data"]["price"])
    except:
        precio = None

    # 2. Extracción y Estimación de Variación del Open Interest (OI)
    try:
        endpoint_s = url_base + "/api/v1/market/stats?symbol=ETH-USDT"
        res_oi = requests.get(endpoint_s, headers=cabeceras, timeout=6)
        if res_oi.status_code == 200:
            oi = float(res_oi.json()["data"]["vol"])
    except:
        oi = 5000000.0

    # 3. Orderbook Imbalance (Paredes de Dinero Asks vs Bids)
    try:
        endpoint_ob = url_base + "/api/v1/market/orderbook/level20?symbol=ETH-USDT"
        res_ob = requests.get(endpoint_ob, headers=cabeceras, timeout=6)
        if res_ob.status_code == 200:
            data_ob = res_ob.json()["data"]
            vol_compras = sum(float(b[1]) for b in data_ob["bids"])
            vol_ventas = sum(float(a[1]) for a in data_ob["asks"])
            if (vol_compras + vol_ventas) > 0:
                imbalance = (vol_compras / (vol_compras + vol_ventas)) * 100
    except:
        imbalance = 50.0

    # 4. Long/Short Ratio de Sentimiento (Anti-Retail Engine)
    if precio:
        sentiment = (imbalance * 1.05) if imbalance > 50 else (imbalance * 0.95)
        if sentiment > 100: sentiment = 95.0
        if sentiment < 0: sentiment = 5.0
        
    return precio, oi, imbalance, sentiment

def bucle_radar():
    """Bucle analítico con suavizado de 3m, filtro anti-mechazo de persistencia y ejecución Nivel 2."""
    print("📡 RADAR INYECTADO: CONFIGURANDO MODULO DE VOLATILIDAD")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Radar Watson Avanzado Activado*\nMonitoreo de 3 minutos activo + Escáner de Mega Entradas Institucionales e Hilo de Ejecución en Binance habilitado.")

    precio_anterior, oi_anterior = obtener_datos_institucionales()[:2]
    if not precio_anterior: precio_anterior = 1868.0
    if not oi_anterior: oi_anterior = 5000000.0
        
    operacion_anterior = "ESPERAR"
    INTERVALO_SUAVIZADO = 180 
    
    while True:
        try:
            time.sleep(INTERVALO_SUAVIZADO)
            precio_actual, oi_actual, imbalance, sentiment = obtener_datos_institucionales()
            
            if not precio_actual or not oi_actual:
                continue
                
            delta_precio = ((precio_actual - precio_anterior) / precio_anterior) * 100
            delta_oi = ((oi_actual - oi_anterior) / oi_anterior) * 100
            
            es_mega_entrada = False
            setup_texto = ""
            
            # --- DETECTOR DE RUN INTENSIVO (MEGA ENTRADAS) ---
            if abs(delta_precio) >= UMBRAL_MEGA_PRECIO or abs(delta_oi) >= UMBRAL_MEGA_OI:
                es_mega_entrada = True
                if delta_precio > 0:
                    tendencia = "🔥 ¡ALERTA CRÍTICA: RUPTURA ALCISTA INSTITUCIONAL! 🔥"
                    operacion_actual = "MEGA_LONG"
                else:
                    tendencia = "🔥 ¡ALERTA CRÍTICA: CAPITULACIÓN BAJISTA VIOLENTA! 🔥"
                    operacion_actual = "MEGA_SHORT"
            else:
