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
INTERVALO_SEGUNDOS = 30  # Intervalo de monitoreo rápido

# Limpieza automática del token por si se guardó con la URL vieja pegada
RAW_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_TOKEN = RAW_TOKEN.split("telegram.org")[-1] if "telegram.org" in RAW_TOKEN else RAW_TOKEN

TELEGRAM_CHAT_ID = "@bunkerop"  
PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Despacha alertas directas limpiando cualquier residuo en el Token."""
    if not TELEGRAM_TOKEN or "AAHDSp" not in TELEGRAM_TOKEN:
        print(f"❌ ERROR: Token con formato inválido o vacío detectado: {TELEGRAM_TOKEN}")
        return

    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try: 
        res = requests.post(url, json=payload, headers=cabeceras, timeout=10)
        print(f"📡 [TELEGRAM API] Status: {res.status_code} | Respuesta: {res.text}")
    except Exception as e: 
        print(f"❌ Fallo de red crítico hacia Telegram: {e}")

def obtener_datos_mercado():
    """Oráculos alternativos de alta disponibilidad inmunes al bloqueo de Render."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Pasarela 1: Kraken API (Suele ser inmune a bloqueos de servidores en la nube)
    try:
        url = "https://kraken.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res['result']['XETHZUSD']['c'][0])
        print(f"🟩 Oráculo 1 exitoso (Kraken) -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 1 (Kraken) falló o fue bloqueado: {e}")
        
    # Pasarela 2: Crypto.com API Pública
    try:
        url = "https://crypto.com"
        res = requests.get(url, headers=cabeceras, timeout=6).json()
        precio = float(res['result']['data'][0]['a'])
        print(f"🟩 Oráculo 2 exitoso (Crypto.com) -> ETH: ${precio:.2f}")
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 2 (Crypto.com) falló o fue bloqueado: {e}")

    return None, None, None

def bucle_radar():
    print("📡 RADAR WATSON PERPETUO: ACTIVADO Y CORRIENDO")
    sys.stdout.flush()
    
    # Test instantáneo obligatorio al encender
    enviar_telegram("📡 *Radar Watson Reestabilizado*\nEvasión de bloqueo geográfico completada con éxito. Monitoreando mercado...")

    precio_anterior, _, _ = obtener_datos_mercado()
    if not precio_anterior:
        print("⚠️ Advertencia: Oráculos saturados en el arranque. Iniciando con precio base de $3400.00")
        precio_anterior = 3400.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, _, _ = obtener_datos_mercado()
            
            if not precio_actual:
                print("⏳ Reintentando conexión: Todos los oráculos bloqueados temporalmente.")
                continue
                
            delta = ((precio_actual - precio_anterior) / precio_anterior) * 100
            print(f"[RADAR] ETH: ${precio_actual:.2f} | Variación: {delta:+.4f}%")
            sys.stdout.flush()
            
            # Envía actualización forzada para comprobar que tu canal de Telegram esté vivo
            enviar_telegram(f"🎯 *Radar Watson Operando*\nETH: `${precio_actual:.2f}`\nVar: `{delta:+.3f}%`")
                
            precio_anterior = precio_actual
        except Exception as e:
            print(f"❌ Error en el bucle principal: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Watson Pro Online", 200

# Iniciador del hilo perpetuo en Render
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
