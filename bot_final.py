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

# EXTRACTOR ULTRA-SEGURO: Limpa cualquier texto basura, URLs pegadas o espacios
RAW_ENV = os.environ.get("TELEGRAM_TOKEN", "").strip()
# Busca el patrón exacto del token de Telegram (números seguidos de dos puntos y caracteres alfanuméricos)
TOKEN_MATCH = re.search(r"(\d+:[\w-]+)", RAW_ENV)

if TOKEN_MATCH:
    TELEGRAM_TOKEN = TOKEN_MATCH.group(1)
else:
    # Si falla la expresión regular, intentamos limpiar manualmente los residuos comunes
    TELEGRAM_TOKEN = RAW_ENV.replace("https://telegram.org", "").replace("telegram.org", "").strip()

TELEGRAM_CHAT_ID = "@bunkerop"  
PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Despacha alertas garantizando la construcción perfecta de la API oficial."""
    print(f"📡 [DIAGNÓSTICO] Token utilizado actualmente: {TELEGRAM_TOKEN[:10]}...[OCULTO]")
    
    if not TELEGRAM_TOKEN or "api" in TELEGRAM_TOKEN or "telegram" in TELEGRAM_TOKEN:
        print("❌ ERROR CRÍTICO: El Token sigue dañado o contiene texto de URL inválido.")
        return

    # Construcción limpia de la API oficial de bots
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try: 
        print(f"🔗 [DIAGNÓSTICO] URL de destino final: https://telegram.org[TOKEN_OCULTO]/sendMessage")
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print(f" Response Status: {res.status_code} | Contenido: {res.text}")
    except Exception as e: 
        print(f"❌ Fallo de red hacia los servidores de Telegram: {e}")

def obtener_datos_mercado():
    """Oráculos globales de alta disponibilidad e inmunes al bloqueo regional de Render."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Pasarela 1: Kraken API (Inmune a bloqueos en la nube)
    try:
        url = "https://kraken.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res['result']['XETHZUSD']['c'][0])
        print(f"🟩 Oráculo 1 (Kraken) exitoso -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 1 (Kraken) no disponible: {e}")
        
    # Pasarela 2: Crypto.com API Pública
    try:
        url = "https://crypto.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res['result']['data'][0]['a'])
        print(f"🟩 Oráculo 2 (Crypto.com) exitoso -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 2 (Crypto.com) no disponible: {e}")

    return None, None, None

def bucle_radar():
    print("📡 RADAR WATSON GLOBAL PERPETUO ACTIVADO")
    sys.stdout.flush()
    
    # Test forzado de arranque
    enviar_telegram("📡 *Radar Watson Reestabilizado*\nEvasión de restricciones completada. Monitoreando mercado 24/7...")

    precio_anterior, _, _ = obtener_datos_mercado()
    if not precio_anterior:
        precio_anterior = 3400.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Reintentando conexión con los oráculos...")
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[MONITOREO] ETH: ${precio_actual:.2f} | Var: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Envío automático de prueba para certificar el canal
            enviar_telegram(f"🎯 *Actualización Radar Watson*\nETH: `${precio_actual:.2f}`\nVar: `{delta:+.3f}%`")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Watson Pro Activado Persistente", 200

# Lanzamiento seguro del subproceso en segundo plano
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
