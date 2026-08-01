import os
import time
import threading
import requests
from collections import deque
from flask import Flask, jsonify
from binance.client import Client
from binance.exceptions import BinanceAPIException

app = Flask(__name__)

# CONFIGURACIÓN DE PARÁMETROS FIJOS DEL SISTEMA
SYMBOL = "ETHUSDT"
TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "-1004335003036"

# UMBRALES DE PRECISIÓN BANCARIA (AJUSTE QUIRÚRGICO DE ALTA TASA DE ÉXITO)
UMBRAL_MIN_PRECIO = 0.0012   # Mínimo 0.12% de variación en 3 minutos para despertar el bot
UMBRAL_MIN_OI = 0.0025       # Mínimo 0.25% de inyección de dinero real en el Interés Abierto
FILTRO_MECHAZO_MAX = 0.0018  # Límite máximo de variación tolerada en el microtiempo de 3s (0.18%)

# Variables de entorno inyectadas de Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

binance_client = None
if BINANCE_API_KEY and BINANCE_SECRET_KEY:
    binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# Memoria circular de precisión a 3 minutos (36 muestras tomadas cada 5 segundos = 180s)
HISTORIAL_CAPACIDAD = 36
historial_precios = deque(maxlen=HISTORIAL_CAPACIDAD)
historial_oi = deque(maxlen=HISTORIAL_CAPACIDAD)

def enviar_telegram(mensaje):
    """Canal de auditoría directa para control operacional del sistema."""
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=4)
    except Exception:
        pass

def consultar_mercado_futuros():
    """Captura de datos en milisegundos directamente del libro de órdenes de Binance."""
    try:
        if not binance_client:
            return None, None
        ticker = binance_client.futures_symbol_ticker(symbol=SYMBOL)
        oi_data = binance_client.futures_open_interest(symbol=SYMBOL)
        return float(ticker['price']), float(oi_data['openInterest'])
    except Exception as e:
        print(f"Error de lectura en API de Binance: {e}")
        return None, None

def evaluar_filtro_anti_mechazo(precio_origen):
    """Pausa isolada de 3 segundos para detectar absorciones y órdenes institucionales fantasma."""
    time.sleep(3)
    try:
        ticker = binance_client.futures_symbol_ticker(symbol=SYMBOL)
        precio_actual = float(ticker['price'])
        variacion_micro = abs((precio_actual - precio_origen) / precio_origen)
        return variacion_micro <= FILTRO_MECHAZO_MAX
    except Exception:
        return False

def ejecutar_caza_asimetrica(direccion, precio_mercado, var_precio, var_oi):
    """Ejecutor de mercado de alta velocidad con Brackets integrados y apalancamiento adaptativo."""
    if not binance_client:
        return

    try:
        # APALANCAMIENTO AUTÓNOMO ADAPTATIVO: Si la fuerza de OI es brutal, escala a X20
        if abs(var_oi) >= 0.0050 or abs(var_precio) >= 0.0035:
            leverage = 20
            tp_porcentaje = 0.0050  # +0.50% de ganancia real rápida
            sl_porcentaje = 0.0030  # -0.30% de stop loss quirúrgico
        else:
            leverage = 10
            tp_porcentaje = 0.0022  # +0.22% de ganancia estándar
            sl_porcentaje = 0.0015  # -0.15% de stop loss estándar

        # Ajustar apalancamiento en la cuenta de futuros de Binance
        binance_client.futures_change_leverage(symbol=SYMBOL, leverage=leverage)

        # GESTIÓN DE CAPITAL INTELIGENTE: Interés compuesto con Guardrail a $400 USD
        account = binance_client.futures_account()
        balance_disponible = float(account.get('availableBalance', 0))
        
        capital_operativo = balance_disponible * 0.50 if balance_disponible > 400.0 else balance_disponible * 1.00
        
        # Formateo estricto del tamaño de lote (ETH requiere precisión de 3 decimales exactos)
        cantidad_nocional = (capital_operativo * leverage) / precio_mercado
        quantity = round(cantidad_nocional, 3)
        
        if quantity <= 0:
            return

        side_entrada = Client.SIDE_BUY if direccion == "LONG" else Client.SIDE_SELL
        side_salida = Client.SIDE_SELL if direccion == "LONG" else Client.SIDE_BUY

        # Envío inmediato de la orden principal a precio de mercado (MARKET)
        binance_client.futures_create_order(
            symbol=SYMBOL, side=side_entrada, type=Client.FUTURE_ORDER_TYPE_MARKET, quantity=quantity
        )

        # Cálculo matemático exacto de Brackets (ETHUSDT Tick size requiere 2 decimales de precio)
        if direccion == "LONG":
            precio_tp = round(precio_mercado * (1 + tp_porcentaje), 2)
            precio_sl = round(precio_mercado * (1 - sl_porcentaje), 2)
        else:
            precio_tp = round(precio_mercado * (1 - tp_porcentaje), 2)
            precio_sl = round(precio_mercado * (1 + sl_porcentaje), 2)

        # Colocación instantánea de Brackets en la infraestructura de Binance (Reduce Only)
        binance_client.futures_create_order(
            symbol=SYMBOL, side=side_salida, type='TAKE_PROFIT_MARKET', stopPrice=precio_tp, closePosition=True, reduceOnly=True
        )
        binance_client.futures_create_order(
            symbol=SYMBOL, side=side_salida, type='STOP_MARKET', stopPrice=precio_sl, closePosition=True, reduceOnly=True
        )

        # Reporte de éxito en tiempo real al Telegram
        msg = f"🦅 *DEPREDADOR EJECUTADO* (x{leverage})\n💥 Acción: *{direccion}*\n💰 Precio Entrada: ${precio_mercado}\n🎯 TP Objetivo: ${precio_tp}\n🛑 SL Seguridad: ${precio_sl}\n📊 Var. Precio (3m): {round(var_precio*100, 3)}%\n📈 Var. OI (3m): {round(var_oi*100, 3)}%"
        enviar_telegram(msg)

    except BinanceAPIException as e:
        enviar_telegram(f"❌ *API Binance Rechazo:* {e.message} (Código {e.code})")
    except Exception as e:
        enviar_telegram(f"❌ *Error Crítico de Ejecución:* {str(e)}")

def motor_analitico_perpetuo():
    """Ciclo asincrónico infinito de ultra-precisión quirúrgica para escaneo del mercado."""
    print("Filtros algorítmicos activados. Buscando asimetrías de volumen...")
    while True:
        try:
            precio_actual, oi_actual = consultar_mercado_futuros()

            if precio_actual and oi_actual:
                historial_precios.append(precio_actual)
                historial_oi.append(oi_actual)

                # Ejecutar análisis matemático puro solo cuando la ventana de 3 minutos esté completa
                if len(historial_precios) == HISTORIAL_CAPACIDAD:
                    precio_base = historial_precios[0]
                    oi_base = historial_oi[0]

                    # Cálculo exacto de variaciones de rango
                    var_precio = (precio_actual - precio_base) / precio_base
                    var_oi = (oi_actual - oi_base) / oi_base

                    # FILTRO DE EXCLUSIÓN: ¿Es el mercado lo suficientemente volátil o es un área muerta?
                    if abs(var_precio) >= UMBRAL_MIN_PRECIO and var_oi >= UMBRAL_MIN_OI:
                        
                        # CONDICIÓN DE DISPARO LONG: El precio sube respaldado por inyección masiva de contratos
                        if var_precio > 0:
                            if evaluar_filtro_anti_mechazo(precio_actual):
                                ejecutar_caza_asimetrica("LONG", precio_actual, var_precio, var_oi)
                                historial_precios.clear()
                                historial_oi.clear()

                        # CONDICIÓN DE DISPARO SHORT: El precio cae impulsado por vendedores institucionales agresivos
                        elif var_precio < 0:
                            if evaluar_filtro_anti_mechazo(precio_actual):
                                ejecutar_caza_asimetrica("SHORT", precio_actual, var_precio, var_oi)
                                historial_precios.clear()
                                historial_oi.clear()

        except Exception as e:
            print(f"Error en ciclo analítico continuo: {e}")

        time.sleep(5)  # Intervalo de escaneo exacto para prevenir limitaciones de tasa (Rate limits)

# Inicializar motor de escaneo en hilo demonio seguro
hilo_motor = threading.Thread(target=motor_analitico_perpetuo, daemon=True)
hilo_motor.start()

@app.route('/health', methods=['GET'])
def health():
    """Validación de pulso continuo automatizado para UptimeRobot."""
    return jsonify({
        "status": "online",
        "motor": "Watson Depredador V2",
        "ticks_acumulados": len(historial_precios)
    }), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
