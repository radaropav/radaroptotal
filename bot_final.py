import os
import time
import requests
from flask import Flask, request, jsonify
from binance.client import Client
from binance.exceptions import BinanceAPIException

app = Flask(__name__)

# CONFIGURACIÓN DE CREDENCIALES FIJAS INYECTADAS
SYMBOL = "ETHUSDT"
TELEGRAM_TOKEN = "8991347344:AAHDSp718hsWqd8uxceBN9D0_n5ZXqR6V1Q"
TELEGRAM_CHAT_ID = "-1004335003036"

# CREDENCIALES DE ENTORNO EN RENDER
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Inicialización segura de Binance Client
binance_client = None
if BINANCE_API_KEY and BINANCE_SECRET_KEY:
    binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def enviar_telegram(mensaje):
    """Envía notificaciones de auditoría directamente al canal público."""
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error de Telegram: {e}")

def obtener_datos_oraculo():
    """Oráculo Descentralizado: Extrae el precio de mercado base de GateIO para evitar latencias."""
    try:
        response = requests.get(f"https://gateio.ws{SYMBOL.replace('USDT', '_USDT')}", timeout=4)
        if response.status_code == 200:
            data = response.json()
            return float(data[0]['last'])
    except Exception:
        pass
    
    # Fallback si GateIO no responde
    try:
        if binance_client:
            ticker = binance_client.futures_symbol_ticker(symbol=SYMBOL)
            return float(ticker['price'])
    except Exception as e:
        print(f"Error en Oráculo: {e}")
    return None

def validar_estabilidad_precio(precio_inicial):
    """Filtro Anti-Mechazos Isolado (Evita trampas de bots / spoofing)."""
    time.sleep(3)
    precio_final = obtener_datos_oraculo()
    if not precio_final:
        return False
    
    variacion = abs((precio_final - precio_inicial) / precio_inicial)
    if variacion > 0.0020:  # Mayor a 0.20%
        return False
    return True

def calcular_capital_orden(balance_actual):
    """Interés compuesto automático con Guardrail de seguridad a $400 USD."""
    if balance_actual > 400.0:
        return balance_actual * 0.50  # Reduce riesgo al 50%
    return balance_actual * 1.00  # Usa el 100% (~$80 USD iniciales)

def ejecutar_brackets_binance(direccion, precio, variacion_senial):
    """Ejecuta orden de mercado con brackets acoplados (TP/SL) y reduceOnly activo."""
    if not binance_client:
        return "Cliente Binance no configurado en variables de entorno."

    try:
        # 1. Definición de Setup y Apalancamiento Dinámico según fuerza de la variación
        if variacion_senial >= 0.40:
            leverage, tp_pct, sl_pct = 20, 0.0050, 0.0030  # Mega Entrada (TP: +0.50% / SL: -0.30%)
        else:
            leverage, tp_pct, sl_pct = 10, 0.0022, 0.0015  # Operación Estándar (TP: +0.22% / SL: -0.15%)

        binance_client.futures_change_leverage(symbol=SYMBOL, leverage=leverage)
        
        # 2. Balance e interés compuesto para determinar cantidad
        account_info = binance_client.futures_account()
        balance_actual = float(account_info.get('availableBalance', 0))
        capital_riesgo = calcular_capital_orden(balance_actual)
        
        # Cantidad nocional calculando el apalancamiento
        quantity = round((capital_riesgo * leverage) / precio, 3)
        if quantity <= 0:
            return f"Capital insuficiente para operar: {balance_actual} USD"

        # 3. Disparar Orden Principal al Mercado (MARKET)
        side_principal = Client.SIDE_BUY if direccion == "LONG" else Client.SIDE_SELL
        side_cobertura = Client.SIDE_SELL if direccion == "LONG" else Client.SIDE_BUY
        
        orden_market = binance_client.futures_create_order(
            symbol=SYMBOL,
            side=side_principal,
            type=Client.FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )

        # 4. Calcular precios exactos de Brackets
        if direccion == "LONG":
            tp_price = round(precio * (1 + tp_pct), 2)
            sl_price = round(precio * (1 - sl_pct), 2)
        else:
            tp_price = round(precio * (1 - tp_pct), 2)
            sl_price = round(precio * (1 + sl_pct), 2)

        # 5. Enviar Órdenes Bracket con reduceOnly=True
        binance_client.futures_create_order(
            symbol=SYMBOL,
            side=side_cobertura,
            type='TAKE_PROFIT_MARKET',
            stopPrice=tp_price,
            closePosition=True,
            reduceOnly=True
        )
        
        binance_client.futures_create_order(
            symbol=SYMBOL,
            side=side_cobertura,
            type='STOP_MARKET',
            stopPrice=sl_price,
            closePosition=True,
            reduceOnly=True
        )

        msg = f"🚀 *{direccion} Ejecutado* x{leverage}\n💰 Precio: {precio}\n📦 Qty: {quantity}\n🎯 TP: {tp_price}\n🛑 SL: {sl_price}"
        enviar_telegram(msg)
        return "Operación ejecutada con Brackets correctamente."

    except BinanceAPIException as e:
        error_msg = f"❌ *Error Binance API:* {e.message} (Código {e.code})"
        enviar_telegram(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ *Error crítico:* {str(e)}"
        enviar_telegram(error_msg)
        return error_msg

@app.route('/webhook', methods=['POST'])
def webhook():
    """Punto de entrada plano y lineal para procesar señales externas sin fallos de indentación."""
    data = request.get_json() or {}
    direccion = data.get("direccion")  # "LONG" o "SHORT"
    variacion_senial = float(data.get("variacion", 0.0)) # Variación porcentual de la señal

    if direccion not in ["LONG", "SHORT"]:
        return jsonify({"status": "ignorado", "reason": "Dirección inválida"}), 400

    precio_oraculo = obtener_datos_oraculo()
    if not precio_oraculo:
        return jsonify({"status": "error", "reason": "Oráculo no disponible"}), 500

    # Filtro anti-mechazos
    if not validar_estabilidad_precio(precio_oraculo):
        enviar_telegram(f"⚠️ *Disparo Cancelado:* Inestabilidad o Mechazo detectado en {SYMBOL}.")
        return jsonify({"status": "cancelado", "reason": "Filtro anti-mechazos activado"}), 200

    # Ejecución directa de la orden en Binance Futures
    resultado = ejecutar_brackets_binance(direccion, precio_oraculo, variacion_senial)
    return jsonify({"status": "procesado", "resultado": resultado}), 200

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para el pulso de UptimeRobot."""
    return jsonify({"status": "active", "bot": "Watson V2"}), 200

if __name__ == '__main__':
    # Render asigna el puerto mediante la variable de entorno PORT, fallback al puerto 10000
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
