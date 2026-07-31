import time
import requests
import threading
import os
import sys
import json
import base64
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA NATIVA INDESTRUCTIBLE
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

# Credenciales físicas directas para la salida de Telegram
TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "@bunkerop"  

PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Envío nativo estructurado hacia la API de Telegram."""
    if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
        print("❌ ERROR: Estructura de token vacía o rota.")
        sys.stdout.flush()
        return

    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code} | Respuesta: {res.text}")
        sys.stdout.flush()
    except Exception as e: 
        print(f"❌ Fallo crítico de red hacia Telegram: {e}")
        sys.stdout.flush()

def obtener_datos_mercado():
    """Extracción de precios usando decodificación en memoria inmune a alteraciones."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # ORÁCULO 1: CryptoCompare público directo (Sustituye al saturado CoinGecko)
    try:
        # URL oculta: 'https://cryptocompare.com'
        url_b64_1 = "aHR0cHM6Ly9taW4tYXBpLmNyeXB0b2NvbXBhcmUuY29tL2RhdGEvcHJpY2U/ZnN5bT1FVEgmdHN5bXM9VVNE"
        endpoint_1 = base64.b64decode(url_b64_1).decode('utf-8')
        
        res = requests.get(endpoint_1, headers=cabeceras, timeout=8).json()
        precio = float(res['USD'])
        print(f"🟩 HACK EXITOSO (CryptoCompare Directo) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo Pasarela 1 inaccesible: {e}")
        sys.stdout.flush()

    # ORÁCULO 2: Endpoint espejo global de Binance (api3 sin geobloqueo)
    try:
        # URL oculta: 'https://binance.com'
        url_b64_2 = "aHR0cHM6Ly9hcGkzLmJpbmFuY2UuY29tL2FwaS92My90aWNrZXIvcHJpY2U/c3ltYm9sPUVUSFVTRFQ="
        endpoint_2 = base64.b64decode(url_b64_2).decode('utf-8')
        
        res = requests.get(endpoint_2, headers=cabeceras, timeout=8).json()
        precio = float(res['price'])
        print(f"🟩 HACK EXITOSO (Binance Mirror Directo) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo Pasarela 2 inaccesible: {e}")
        sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Hilo de ejecución continuo aislado y optimizado para Render."""
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
                print("⏳ Oráculos saturados o bloqueados temporalmente. Reintentando...")
                sys.stdout.flush()
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[RADAR] ETH: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Notificación de variación de precio enviada directamente al canal público
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: {delta:+.3f}%")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en ejecución del radar: {e}")
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Inicialización segura en segundo plano para evitar bloqueos de Render
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
