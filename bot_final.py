import time
import requests
import threading
import os
import sys
import json
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA DIRECTA (CANAL PÚBLICO - ALIAS DIRECTO)
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

# Credenciales físicas inyectadas directamente sin mutaciones
TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "@bunkerop"  # Alias del canal público obligatorio

PORCENTAJE_SL = 0.0015  
PORCENTAJE_TP = 0.0022  

def enviar_telegram(mensaje):
    """Bypass regional utilizando espejos dinámicos con timeouts ultra-agresivos para Render."""
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Banco de rutas de evasión alternativas
    url_espejo_1 = f"https://telegram-proxy.org{TELEGRAM_TOKEN}/sendMessage"
    url_espejo_2 = f"https://teleapi.net{TELEGRAM_TOKEN}/sendMessage"
    url_oficial = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"

    # Reducimos el timeout a 3 segundos para evitar que Render congele el hilo secundario
    for indice, url in enumerate([url_espejo_1, url_espejo_2, url_oficial], start=1):
        try:
            print(f"🚀 Enviando alerta vía Canal de Evasión #{indice}... (Timeout: 3s)")
            sys.stdout.flush()
            
            res = requests.post(url, json=payload, headers=cabeceras, timeout=3)
            
            if res.status_code == 200:
                print(f"🟩 [TELEGRAM] Mensaje entregado con éxito en Canal #{indice}!")
                sys.stdout.flush()
                return
            else:
                print(f"⚠️ Canal #{indice} rechazó la entrega. Status: {res.status_code} | Info: {res.text[:100]}")
                sys.stdout.flush()
        except requests.exceptions.Timeout:
            print(f"⏳ Canal #{indice} descartado por Timeout (Superó los 3 segundos).")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Canal #{indice} inaccesible por error crítico: {e}")
            sys.stdout.flush()
            
    print("🚨 [CRÍTICO] Fin de ciclo: Ninguna ruta pudo conectar en esta iteración.")
    sys.stdout.flush()

def obtener_datos_mercado():
    """Bypassea restricciones geográficas extrayendo datos estructurados de feeds alternativos."""
    cabeceras = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Oráculo 1: CoinGecko encapsulado correctamente a través de la API AllOrigins
    try:
        url_target = "https://coingecko.com"
        proxy_url = f"https://allorigins.win{requests.utils.quote(url_target)}"
        
        res = requests.get(proxy_url, headers=cabeceras, timeout=5).json()
        data_limpia = json.loads(res['contents'])
        precio = float(data_limpia['ethereum']['usd'])
        print(f"🟩 ORÁCULO 1 COMPILADO -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 1 (CoinGecko Proxy) inaccesible: {e}")
        sys.stdout.flush()

    # Oráculo 2: API pública simplificada de Binance (Endpoint alternativo asiático sin restricciones)
    try:
        # api3 rutea el tráfico ignorando los geobloqueos regionales comunes del dominio principal
        url_binance = "https://binance.com"
        res = requests.get(url_binance, headers=cabeceras, timeout=5).json()
        precio = float(res['price'])
        print(f"🟩 ORÁCULO 2 COMPILADO (Binance Mirror) -> ETH: ${precio:.2f}")
        sys.stdout.flush()
        return precio, 5000000.0, 15000000.0
    except Exception as e:
        print(f"⚠️ Oráculo 2 (Binance Mirror) inaccesible: {e}")
        sys.stdout.flush()

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
                print("⏳ Oráculos saturados o bloqueados temporalmente. Reintentando...")
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

# Inicialización segura en segundo plano
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
