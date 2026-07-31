import time
import requests
import threading
import os
import sys
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN ULTRA-SENSITIVA PERPETUA
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  # Bajado a 30 para probar más rápido

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "@bunkerop"  

PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Despacha alertas e imprime la respuesta exacta de los servidores de Telegram."""
    print(f"[DIAGNÓSTICO] Intentando enviar a Telegram: {mensaje[:30]}...")
    if not TELEGRAM_TOKEN:
        print("❌ ERROR CRÍTICO: El TELEGRAM_TOKEN está vacío en las variables de Render.")
        return

    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=8)
        print(f"[TELEGRAM RESPONSE] Código: {res.status_code} | Respuesta: {res.text}")
    except Exception as e: 
        print(f"❌ Fallo de red directo hacia Telegram: {e}")

def obtener_datos_mercado():
    """Oráculo con timeouts cortos para evitar que el hilo se congele."""
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    # Intento 1: Binance API Internacional Directa
    try:
        print("[ORÁCULO] Probando Endpoint 1 (Binance)...")
        url = "https://binance.com"
        res = requests.get(url, headers=cabeceras, timeout=4).json()
        return float(res['price']), 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Endpoint 1 bloqueado o lento: {e}")
        
    # Intento 2: Binance US (Espejo alternativo por si Render está en Ohio/USA)
    try:
        print("[ORÁCULO] Probando Endpoint 2 (Binance US)...")
        url = "https://binance.us"
        res = requests.get(url, headers=cabeceras, timeout=4).json()
        return float(res['price']), 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Endpoint 2 bloqueado o lento: {e}")

    # Intento 3: CoinGecko API Pública
    try:
        print("[ORÁCULO] Probando Endpoint 3 (CoinGecko)...")
        url = "https://coingecko.com"
        res = requests.get(url, headers=cabeceras, timeout=4).json()
        return float(res['ethereum']['usd']), 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Endpoint 3 bloqueado o lento: {e}")

    return None, None, None

def bucle_radar():
    print("📡 BUCLE RADAR INICIADO CORRECTAMENTE EN HILO SECUNDARIO")
    sys.stdout.flush()
    
    # Test forzado inmediato
    enviar_telegram("📡 *Radar Watson Activo*\nVerificando enlace indestructible...")

    precio_anterior, oi_anterior, vol_anterior = obtener_datos_mercado()
    if not precio_anterior:
        print("⚠️ No se pudieron obtener precios iniciales. Usando precio base de contingencia ($3400).")
        precio_anterior = 3400.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Saltando iteración: Todos los oráculos caídos temporalmente.")
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[MONITOREO] ETH Actual: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Forzamos un envío de prueba simulado si la variación es casi nula para verificar Telegram
            if abs(delta) >= 0.0:  
                enviar_telegram(f"🎯 *Actualización en Vivo de Prueba*\nETH: `${precio_actual:.2f}`\nVariación: `{delta:+.3f}%`")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error dentro del bucle: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "OK", 200

# Arrancar el hilo de ejecución garantizando logs visibles
print("[SISTEMA] Lanzando hilo del radar...")
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
