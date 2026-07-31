import time
import requests
import threading
import os
import sys
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA ABSOLUTA - SIN DEPENDENCIAS EXTERNAS
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

# Forzado con ID numérico del canal público para evitar desvíos de alias
TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "-1004335003036"  

def enviar_telegram(mensaje):
    """Envío nativo e independiente sin uso de f-strings en zona crítica."""
    url = "https://telegram.org" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print("📡 [TELEGRAM ESP_REPLY] Status: " + str(res.status_code) + " | " + str(res.text))
        sys.stdout.flush()
    except Exception as e: 
        print("❌ Fallo de red Telegram: " + str(e))
        sys.stdout.flush()

def obtener_datos_mercado():
    """Lógica pura de oráculos de nivel 1 con extracción de datos crudos."""
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    # ORÁCULO 1: KuCoin API pública (Idónea para servidores Cloud en EE.UU.)
    try:
        res = requests.get("https://kucoin.com", headers=cabeceras, timeout=8)
        if res.status_code == 200:
            data = res.json()
            precio = float(data["data"]["price"])
            print("🟩 ORÁCULO 1 (KuCoin) -> ETH: $" + str(precio))
            sys.stdout.flush()
            return precio, 0, 0
    except Exception as e:
        print("⚠️ Pasarela KuCoin descartada: " + str(e))
        sys.stdout.flush()

    # ORÁCULO 2: Gate.io API de tickers spot
    try:
        res = requests.get("https://gateio.ws", headers=cabeceras, timeout=8)
        if res.status_code == 200:
            data = res.json()
            precio = float(data[0]["last"])
            print("🟩 ORÁCULO 2 (GateIO) -> ETH: $" + str(precio))
            sys.stdout.flush()
            return precio, 0, 0
    except Exception as e:
        print("⚠️ Pasarela GateIO descartada: " + str(e))
        sys.stdout.flush()

    return None, None, None

def bucle_radar():
    """Bucle aislado continuo de monitorización."""
    print("📡 RADAR INYECTADO: INICIANDO MONITOR INDESTRUCTIBLE")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Radar Watson Reestabilizado*\nMonitoreando precio en vivo de ETH...")

    precio_anterior, _, _ = obtener_datos_mercado()
    if not precio_anterior:
        precio_anterior = 3430.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Oráculos saturados. Esperando próxima iteración...")
                sys.stdout.flush()
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print("[RADAR] ETH: $" + str(precio_actual) + " | Var: " + str(delta) + "%")
            sys.stdout.flush()
            
            msg = "🎯 *Radar Watson Operando*\nETH: `$" + str(precio_actual) + "`\nVar: " + str(round(delta, 3)) + "%"
            enviar_telegram(msg)
                
            precio_anterior = precio_actual
        except Exception as e:
            print("❌ Error en hilo radar: " + str(e))
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Despliegue en hilo paralelo seguro
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
