import time
import requests
import threading
import os
import sys
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA REAL DE DERIVADOS Y SCALPING
# =====================================================================
SYMBOL = "ETHUSDT"  
INTERVALO_SEGUNDOS = 30  

TOKEN_LIMPIO = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
CHAT_ID_LIMPIO = "-1004335003036"  

# Márgenes para operaciones cortas, rápidas y alcanzables en minutos
PORCENTAJE_SL = 0.0015  # 0.15% para cortar pérdidas rápido
PORCENTAJE_TP = 0.0022  # 0.22% para asegurar ganancias prontas

def enviar_telegram(mensaje):
    """Envío nativo con URL fraccionada de forma simple para evitar mutilaciones."""
    parte1 = 'https://api.'
    parte2 = 'telegram.org/bot'
    parte3 = '/sendMessage'
    
    url_final = parte1 + parte2 + TOKEN_LIMPIO + parte3
    
    payload = {
        "chat_id": CHAT_ID_LIMPIO, 
        "text": mensaje, 
        "parse_mode": "Markdown"
    }
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    try: 
        res = requests.post(url_final, json=payload, headers=cabeceras, timeout=10)
        print("📡 [TELEGRAM] Status: " + str(res.status_code))
        sys.stdout.flush()
    except Exception as e: 
        print("❌ Fallo en enlace de Telegram: " + str(e))
        sys.stdout.flush()

def obtener_datos_mercado_y_oi():
    """Extrae precio e interés abierto estimado a través de APIs redundantes públicas."""
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    precio = None
    oi = None
    
    # URL fraccionada de forma segura
    url_base = 'https://api.' + 'kucoin.com'
    
    # 1. Obtener precio actual de ETH
    try:
        endpoint_p = url_base + "/api/v1/market/orderbook/level1?symbol=ETH-USDT"
        res = requests.get(endpoint_p, headers=cabeceras, timeout=6)
        if res.status_code == 200:
            precio = float(res.json()["data"]["price"])
    except:
        precio = None

    # 2. Obtener estadísticas de contratos de 24h para simular métrica de OI
    try:
        endpoint_s = url_base + "/api/v1/market/stats?symbol=ETH-USDT"
        res_oi = requests.get(endpoint_s, headers=cabeceras, timeout=6)
        if res_oi.status_code == 200:
            oi = float(res_oi.json()["data"]["vol"])
    except:
        oi = 5000000.0  # Respaldo si el servidor no responde rápido
        
    return precio, oi

def bucle_radar():
    """Analiza Precio + OI y genera setups de scalping reales y alcanzables."""
    print("📡 RADAR INYECTADO: INICIANDO MONITOR INDESTRUCTIBLE")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Radar Watson Inteligente Activado*\nMonitoreando Precio, Variación de OI y Setups de Scalping...")

    precio_anterior, oi_anterior = obtener_datos_mercado_y_oi()
    if not precio_anterior:
        precio_anterior = 1868.0
    if not oi_anterior:
        oi_anterior = 5000000.0
    
    while True:
        try:
            time.sleep(INTERVALO_SEGUNDOS)
            precio_actual, oi_actual = obtener_datos_mercado_y_oi()
            
            if not precio_actual or not oi_actual:
                print("⏳ Esperando respuesta estable de los oráculos...")
                sys.stdout.flush()
                continue
                
            delta_precio = ((precio_actual - precio_anterior) / precio_anterior) * 100
            delta_oi = ((oi_actual - oi_anterior) / oi_anterior) * 100
            
            # --- LÓGICA DE DERIVADOS: COMBINACIÓN PRECIO + OI ---
            if delta_precio > 0.005 and delta_oi > 0.01:
                tendencia = "📈 ALCISTA (Confirmación por entrada de capital)"
                operacion = "LONG"
            elif delta_precio < -0.005 and delta_oi > 0.01:
                tendencia = "📉 BAJISTA (Confirmación por presión vendedora)"
                operacion = "SHORT"
            else:
                tendencia = "↕️ ENTORNO NEUTRO / CONSOLIDACIÓN CORTA"
                operacion = "ESPERAR"
                
            # --- OPERACIONES DE SCALPING REALISTAS Y CORTAS ---
            if operacion == "LONG":
                tp_valor = precio_actual * (1 + PORCENTAJE_TP)
                sl_valor = precio_actual * (1 - PORCENTAJE_SL)
                setup_texto = (
                    "🚀 *OPERACIÓN SUGERIDA: ENTRAR EN LONG*\n"
                    "🟢 *Precio Entrada:* `$" + f"{precio_actual:.2f}" + "`\n"
                    "🎯 *Take Profit (Corto):* `$" + f"{tp_valor:.2f}" + "` (+0.22%)\n"
                    "🛑 *Stop Loss (Seguridad):* `$" + f"{sl_valor:.2f}" + "` (-0.15%)\n"
                    "⏱️ _Estrategia: Tomar ganancias rápido en la próxima vela._"
                )
            elif operacion == "SHORT":
                tp_valor = precio_actual * (1 - PORCENTAJE_TP)
                sl_valor = precio_actual * (1 + PORCENTAJE_SL)
                setup_texto = (
                    "🚨 *OPERACIÓN SUGERIDA: ENTRAR EN SHORT*\n"
                    "🔴 *Precio Entrada:* `$" + f"{precio_actual:.2f}" + "`\n"
                    "🎯 *Take Profit (Corto):* `$" + f"{tp_valor:.2f}" + "` (-0.22%)\n"
                    "🛑 *Stop Loss (Seguridad):* `$" + f"{sl_valor:.2f}" + "` (+0.15%)\n"
                    "⏱️ _Estrategia: Tomar ganancias rápido en la próxima vela._"
                )
            else:
                setup_texto = "⏳ *SUGERENCIA: ESPERAR EN COMPRENSIÓN*\n_Razón: Variación débil. Evitar pérdidas innecesarias por comisiones._"

            print("[RADAR] ETH: $" + str(precio_actual) + " | Var OI: " + str(delta_oi) + "%")
            sys.stdout.flush()
            
            # Mensaje con la plantilla de datos completa requerida
            msg = (
                "🎯 *Radar Watson Operando*\n"
                "══════════════════════\n"
                "💰 *Precio ETH:* `$" + f"{precio_actual:.2f}" + "`\n"
                "📊 *Var. Precio (30s):* " + f"{delta_precio:+.3f}" + "%\n"
                "📈 *Var. OI (30s):* " + f"{delta_oi:+.3f}" + "%\n"
                "🔄 *Tipo de Tendencia:* " + tendencia + "\n"
                "══════════════════════\n"
                + setup_texto
            )
            
            enviar_telegram(msg)
            
            precio_anterior = precio_actual
            oi_anterior = oi_actual
            
        except Exception as e:
            print("❌ Error en ejecución del radar: " + str(e))
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

# Lanzamiento seguro del subproceso de fondo
threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
