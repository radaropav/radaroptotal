import time
import requests
import threading
import os
import sys
import json
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN LIMPIA Y COMPILADA DIRECTA
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "@bunkerop"  

PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Envío directo usando la estructura nativa oficial de Telegram."""
    if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
        print("❌ ERROR: Token con formato inválido o vacío.")
        sys.stdout.flush()
        return

    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code} | Respuesta: {res.text}")
        sys.stdout.flush()
    except Exception as e: 
        print(f"❌ Fallo crítico hacia Telegram: {e}")
        sys.stdout.flush()

def obtener_datos_mercado():
    """Bypassea el bloqueo regional usando el endpoint espejo libre api3 de Binance."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # CANAL 1: CryptoCompare Directo (Reemplaza a CoinGecko para evitar bloqueos Cloudflare)
    try:
        url = "https://cryptocompare.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res["USD"])
        print(f"🟩 HACK EXITOSO (CryptoCompare) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Pasarela 1 (CryptoCompare) falló: {e}")
        sys.stdout.flush()

    # CANAL 2: Endpoint api3 de Binance (Libre de geobloqueos geográficos estándar)
    try:
        url_binance = "https://binance.com"
        res = requests.get(url_binance, headers=cabeceras, timeout=6).json()
        precio = float(res["price"])
        print(f"🟩 HACK EXITOSO (Binance Mirror) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Pasarela 2 (Binance Mirror) falló: {e}")
        sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Bucle continuo de monitorización optimizado para Render."""
    print("📡 RADAR INYECTADO: INICIANDO MONITOR INDESTRUCTIBLE")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Radar Watson Reestabilizado*\nHack de evasión regional activado. Monitoreando ETH...")

    precio_anterior, _, _ = obtener_datos_mercado()
    if not precio_anterior:
        precio_anterior = 3400.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Oráculos saturados. Esperando próxima iteración...")
                sys.stdout.flush()
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[RADAR] ETH: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Alerta instantánea formateada limpia
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: {delta:+.3f}%")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Encendido del subproceso en segundo plano
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
