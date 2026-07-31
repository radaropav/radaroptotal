import time
import requests
import threading
import os
import sys
import json
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA NATIVA INDESTRUCTIBLE
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

# Credenciales fijadas en bloques puros para evitar alteraciones de formato
TELEGRAM_TOKEN = "8991347344" + ":" + "AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "@bunkerop"  

PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Envío nativo estructurado por segmentos para asegurar las barras diagonales."""
    if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
        print("❌ ERROR: Estructura de token rota.")
        sys.stdout.flush()
        return

    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    # Construcción segmentada de la URL oficial
    base_api = "https://" + "api.telegram.org"
    endpoint = base_api + "/bot" + TELEGRAM_TOKEN + "/sendMessage"
    
    try: 
        res = requests.post(endpoint, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code} | Respuesta: {res.text}")
        sys.stdout.flush()
    except Exception as e: 
        print(f"❌ Fallo crítico de red hacia Telegram: {e}")
        sys.stdout.flush()

def obtener_datos_mercado():
    """Consumo de oráculos mediante aislamiento de parámetros query de red."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # ORÁCULO 1: Puente AllOrigins con CoinGecko estructurado de forma segura
    try:
        url_target = "https://" + "://coingecko.com"
        proxy_url = "https://" + "api.allorigins.win/get?url=" + requests.utils.quote(url_target)
        
        res = requests.get(proxy_url, headers=cabeceras, timeout=8).json()
        data_limpia = json.loads(res['contents'])
        precio = float(data_limpia['ethereum']['usd'])
        print(f"🟩 HACK EXITOSO (CoinGecko via Proxy) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Hack Pasarela 1 falló: {e}")
        sys.stdout.flush()

    # ORÁCULO 2: Acceso directo al endpoint secundario api3 de Binance (Bypass regional)
    try:
        url_binance = "https://" + "://binance.com"
        res = requests.get(url_binance, headers=cabeceras, timeout=6).json()
        precio = float(res['price'])
        print(f"🟩 HACK EXITOSO (Binance Mirror Directo) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Hack Pasarela 2 falló: {e}")
        sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Hilo de ejecución continuo aislado para Render."""
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
            
            # Formateo de notificación limpia para canal público
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: {delta:+.3f}%")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Inicialización forzada del hilo de fondo
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
