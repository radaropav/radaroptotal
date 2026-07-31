import time
import requests
import threading
import os
import sys
from flask import Flask

app = Flask(__name__)

# =====================================================================
# CONFIGURACIÓN COMPILADA REAL DE DERIVADOS Y SCALPING SUAVIZADO
# =====================================================================
SYMBOL = "ETHUSDT"  

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
        oi = 5000000.0  # Respaldo de seguridad
        
    return precio, oi

def bucle_radar():
    """Bucle con suavizado de tiempo y filtro de confirmación para evitar señales falsas."""
    print("📡 RADAR INYECTADO: CONFIGURANDO FILTRO DE SUAVIZADO")
    sys.stdout.flush()
    
    enviar_telegram("📡 *Módulo de Suavizado Activado*\nVentana de análisis ampliada a 3 minutos con filtro de consistencia para Scalping seguro.")

    precio_anterior, oi_anterior = obtener_datos_mercado_y_oi()
    if not precio_anterior:
        precio_anterior = 1868.0
    if not oi_anterior:
        oi_anterior = 5000000.0
        
    # Variables de memoria para el filtro de consistencia
    operacion_anterior = "ESPERAR"
    
    # Ajustamos el intervalo a 3 minutos (180 segundos) para eliminar el ruido rápido
    INTERVALO_SUAVIZADO = 180 
    
    while True:
        try:
            time.sleep(INTERVALO_SUAVIZADO)
            precio_actual, oi_actual = obtener_datos_mercado_y_oi()
            
            if not precio_actual or not oi_actual:
                continue
                
            delta_precio = ((precio_actual - precio_anterior) / precio_anterior) * 100
            delta_oi = ((oi_actual - oi_anterior) / oi_anterior) * 100
            
            # --- EVALUACIÓN DE DIRECCIÓN CON UMBRAL DE FILTRO ---
            if delta_precio > 0.015 and delta_oi > 0.03:
                tendencia = "📈 ALCISTA (Confirmación por entrada de capital)"
                operacion_actual = "LONG"
            elif delta_precio < -0.015 and delta_oi > 0.03:
                tendencia = "📉 BAJISTA (Confirmación por presión vendedora)"
                operacion_actual = "SHORT"
            else:
                tendencia = "↕️ ENTORNO NEUTRO / CONSOLIDACIÓN CORTA"
                operacion_actual = "ESPERAR"
                
            # --- FILTRO DE CONSISTENCIA DE TRADING ---
            debe_notificar = False
            
            if operacion_actual == "ESPERAR":
                debe_notificar = True
            elif operacion_actual == operacion_anterior:
                debe_notificar = True
            else:
                print("⏳ Tendencia inestable detectada. Filtrando señal...")
                sys.stdout.flush()
                debe_notificar = False

            if debe_notificar:
                # --- MODELADO DE ENTRADAS DE SCALPING REALISTAS ---
                if operacion_actual == "LONG":
                    tp_valor = precio_actual * (1 + PORCENTAJE_TP)
                    sl_valor = precio_actual * (1 - PORCENTAJE_SL)
                    setup_texto = (
                        "🚀 *OPERACIÓN SUGERIDA: ENTRAR EN LONG*\n"
                        "🟢 *Precio Entrada:* `$" + f"{precio_actual:.2f}" + "`\n"
                        "🎯 *Take Profit (Corto):* `$" + f"{tp_valor:.2f}" + "` (+0.22%)\n"
                        "🛑 *Stop Loss (Seguridad):* `$" + f"{sl_valor:.2f}" + "` (-0.15%)\n"
                        "⏱️ _Estrategia: Tendencia confirmada. Buscar salida en la próxima vela._"
                    )
                elif operacion_actual == "SHORT":
                    tp_valor = precio_actual * (1 - PORCENTAJE_TP)
                    sl_valor = precio_actual * (1 + PORCENTAJE_SL)
                    setup_texto = (
                        "🚨 *OPERACIÓN SUGERIDA: ENTRAR EN SHORT*\n"
                        "🔴 *Precio Entrada:* `$" + f"{precio_actual:.2f}" + "`\n"
                        "🎯 *Take Profit (Corto):* `$" + f"{tp_valor:.2f}" + "` (-0.22%)\n"
                        "🛑 *Stop Loss (Seguridad):* `$" + f"{sl_valor:.2f}" + "` (+0.15%)\n"
                        "⏱️ _Estrategia: Tendencia confirmada. Buscar salida en la próxima vela._"
                    )
                else:
                    setup_texto = "⏳ *SUGERENCIA: ESPERAR EN COMPRENSIÓN*\n_Razón: Fluctuación inestable o mercado plano. No arriesgar comisiones._"

                print("[RADAR] ETH: $" + str(precio_actual) + " | Var OI: " + str(delta_oi) + "%")
                sys.stdout.flush()

                msg = (
                    "🎯 *Radar Watson Operando*\n"
                    "══════════════════════\n"
                    "💰 *Precio ETH:* `$" + f"{precio_actual:.2f}" + "`\n"
                    "📊 *Var. Precio (3m):* " + f"{delta_precio:+.3f}" + "%\n"
                    "📈 *Var. OI (3m):* " + f"{delta_oi:+.3f}" + "%\n"
                    "🔄 *Tipo de Tendencia:* " + tendencia + "\n"
                    "══════════════════════\n"
                    + setup_texto
                )
                enviar_telegram(msg)
            
            operacion_anterior = operacion_actual
            precio_anterior = precio_actual
            oi_anterior = oi_actual
            
        except Exception as e:
            print("❌ Error en ejecución del radar: " + str(e))
            sys.stdout.flush()
            time.sleep(5)

@app.route('/')
def home():
    return "📡 Radar Hack Activo", 200

threading.Thread(target=bucle_radar, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
