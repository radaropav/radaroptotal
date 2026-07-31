import time
import requests
import threading
import os
import sys
from flask import Flask

app = Flask(__name__)

SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  
TELEGRAM_CHAT_ID = "@bunkerop"  

# Extracción directa de las pasarelas configuradas desde Render
ENDPOINT_TELEGRAM = os.environ.get("URL_TELEGRAM", "").strip()
ENDPOINT_CRYPTO = os.environ.get("URL_CRYPTO", "").strip()
ENDPOINT_BINANCE = os.environ.get("URL_BINANCE", "").strip()

def enviar_telegram(mensaje):
    """Envío nativo limpio consumiendo la URL externa inyectada."""
    if not ENDPOINT_TELEGRAM:
        print("❌ ERROR CRÍTICO: La variable 'URL_TELEGRAM' no está configurada en Render.")
        sys.stdout.flush()
        return

    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(ENDPOINT_TELEGRAM, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code}")
        sys.stdout.flush()
    except Exception as e: 
        print(f"❌ Fallo crítico de red hacia Telegram: {e}")
        sys.stdout.flush()

def obtener_datos_mercado():
    """Consumo de oráculos mediante variables de entorno inmunes a recortes."""
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    # Oráculo 1: CryptoCompare
    if ENDPOINT_CRYPTO:
        try:
            res = requests.get(ENDPOINT_CRYPTO, headers=cabeceras, timeout=6).json()
            precio = float(res["USD"])
            print(f"🟩 ORÁCULO 1 COMPILADO -> ETH: ${precio:.2f}")
            sys.stdout.flush()
            return precio, 0, 0
        except Exception as e:
            print(f"⚠️ Pasarela 1 falló: {e}")
            sys.stdout.flush()

    # Oráculo 2: Binance Mirror
    if ENDPOINT_BINANCE:
        try:
            res = requests.get(ENDPOINT_BINANCE, headers=cabeceras, timeout=6).json()
            precio = float(res["price"])
            print(f"🟩 ORÁCULO 2 COMPILADO -> ETH: ${precio:.2f}")
            sys.stdout.flush()
            return precio, 0, 0
        except Exception as e:
            print(f"⚠️ Pasarela 2 falló: {e}")
            sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Monitorización continua con volcado de búfer activo."""
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
            
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: {delta:+.3f}%")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
