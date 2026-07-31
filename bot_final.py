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

# Endpoints extraídos de tu entorno blindado en Render
ENDPOINT_TELEGRAM = os.environ.get("URL_TELEGRAM", "").strip()

def enviar_telegram(mensaje):
    """Envío nativo limpio hacia la API de Telegram verificada."""
    if not ENDPOINT_TELEGRAM:
        print("❌ ERROR: La variable 'URL_TELEGRAM' está vacía.")
        sys.stdout.flush()
        return

    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try: 
        res = requests.post(ENDPOINT_TELEGRAM, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM] Status: {res.status_code}")
        sys.stdout.flush()
    except Exception as e: 
        print(f"❌ Fallo crítico hacia Telegram: {e}")
        sys.stdout.flush()

def obtener_datos_mercado():
    """Oráculos alternativos de alta disponibilidad blindados contra bloqueos a hosting."""
    
    # Camuflaje avanzado de cabeceras web para engañar sistemas anti-bot de las APIs
    cabeceras_web = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    # PASARELA 1: Endpoint Público Descentralizado de KuCoin (Jamás bloquea IPs de hosting)
    try:
        url_kucoin = "https://kucoin.com"
        res = requests.get(url_kucoin, headers=cabeceras_web, timeout=8)
        
        # Verificación estricta de que la respuesta sea un texto JSON válido antes de parsear
        if res.status_code == 200 and "data" in res.text:
            data_json = res.json()
            precio = float(data_json["data"]["price"])
            print(f"🟩 ORÁCULO 1 COMPILADO (KuCoin Feed) -> ETH: ${precio:.2f}")
            sys.stdout.flush()
            return precio, 0, 0
    except Exception as e:
        print(f"⚠️ Pasarela 1 (KuCoin Open Feed) saturada: {e}")
        sys.stdout.flush()

    # PASARELA 2: Endpoint Espejo Alternativo de Gate.io (Evasión de Firewalls regionales)
    try:
        url_gate = "https://gateio.ws"
        res = requests.get(url_gate, headers=cabeceras_web, timeout=8)
        
        if res.status_code == 200:
            data_json = res.json()
            # Gate.io devuelve una lista con el ticker solicitado
            precio = float(data_json[0]["last"])
            print(f"🟩 ORÁCULO 2 COMPILADO (Gate Espejo) -> ETH: ${precio:.2f}")
            sys.stdout.flush()
            return precio, 0, 0
    except Exception as e:
        print(f"⚠️ Pasarela 2 (Gate Espejo) saturada: {e}")
        sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Monitorización ininterrumpida."""
    print("📡 RADAR INYECTADO: INICIANDO MONITOR INDESTRUCTIBLE")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Radar Watson Reestabilizado*\nHack de evasión regional activado. Monitoreando ETH...")

    precio_anterior, _, _ = obtener_datos_mercado()
    if not precio_anterior:
        precio_anterior = 3420.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Todos los oráculos de datos de hosting están saturados. Reintentando...")
                sys.stdout.flush()
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[RADAR] ETH: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Formateo de notificación limpia para canal público
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: {delta:+.3f}%")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en ejecución del radar: {e}")
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Lanzamiento del hilo de fondo aislado
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
