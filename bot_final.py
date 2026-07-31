import time
import requests
import threading
import os
import sys
import re
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN ULTRA-SENSITIVA PERPETUA
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

# TOKEN FORZADO: Limpieza absoluta de cualquier residuo
RAW_ENV = os.environ.get("TELEGRAM_TOKEN", "").strip()
TOKEN_MATCH = re.search(r"(\d+:[\w-]+)", RAW_ENV)
TELEGRAM_TOKEN = TOKEN_MATCH.group(1) if TOKEN_MATCH else RAW_ENV.replace("https://telegram.org", "").replace("telegram.org", "").strip()

TELEGRAM_CHAT_ID = "@bunkerop"  
PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Construcción nativa y directa hacia la API oficial de bots sin usar variables externas."""
    if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
        print(f"❌ ERROR: Token con formato inválido o vacío: {TELEGRAM_TOKEN}")
        return

    # URL oficial cableada de forma estricta en el código fuente
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code} | Respuesta: {res.text}")
    except Exception as e: 
        print(f"❌ Fallo crítico hacia Telegram: {e}")

def obtener_datos_mercado():
    """Bypassea el bloqueo de Render inyectando la petición a través de un proxy proxy/wrapper."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # CANAL HACK 1: CoinGecko encapsulado en pasarela CORS bypass (AllOrigins)
    try:
        url_target = "https://coingecko.com"
        proxy_url = f"https://allorigins.win{requests.utils.quote(url_target)}"
        
        res = requests.get(proxy_url, headers=cabeceras, timeout=8).json()
        # AllOrigins devuelve la respuesta original dentro de una cadena string de un campo llamado 'contents'
        import json
        data_limpia = json.loads(res['contents'])
        precio = float(data_limpia['ethereum']['usd'])
        print(f"🟩 HACK EXITOSO (CoinGecko via Proxy) -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Hack Pasarela 1 falló: {e}")

    # CANAL HACK 2: Feed alternativo ultra-rápido de precio indexado (Mesa de dinero)
    try:
        url = "https://cryptocompare.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res['USD'])
        print(f"🟩 HACK EXITOSO (CryptoCompare Directo) -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Hack Pasarela 2 falló: {e}")

    return None, None, None

def bucle_radar():
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
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[RADAR] ETH: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Notificación instantánea forzada
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: `{delta:+.3f}%`")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
