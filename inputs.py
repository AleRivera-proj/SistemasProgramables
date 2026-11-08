import network
import time
import math
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C
from MPU6050 import MPU6050 

i2c = I2C(0, scl=Pin(22), sda=Pin(21),freq=400000)
mpu = MPU6050(i2c)

# --- 1. CONFIGURACIÓN DE RED ---
SSID = "Moka&GizmoHouse"
PASSWORD = "jasaso05"

# --- 2. CONFIGURACIÓN MQTT (Broker Mosquitto) ---
MQTT_BROKER = "192.168.68.118" 
MQTT_USER = "admin"
MQTT_PASSWORD = "MiClave2026"
MQTT_TOPIC = b"juego/controles/"
MQTT_CLIENT_ID = "esp32_mando"

# --- 3. CONFIGURACIÓN DE INCLINACIÓN ---
MAX_INCLINACION_GRADOS = 45.0 

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print('.', end='')
    print('\nConectado a WiFi. IP:', wlan.ifconfig()[0])

def conectar_mqtt():
    print("Conectando al broker MQTT...")
    cliente = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    cliente.connect()
    print("Conectado a MQTT.")
    return cliente

# --- INICIALIZACIÓN ---
conectar_wifi()
cliente_mqtt = conectar_mqtt()

# --- BUCLE PRINCIPAL ---
while True:
    try:
        aceleracion = mpu.read_accel_data(g=True)
        
        ax = aceleracion["x"]
        ay = aceleracion["y"]
        az = aceleracion["z"]
        
        # B. Calcular ángulo. (Centro = 0 grados)
        angulo_rad = math.atan2(ay, ax) 
        angulo_grados = angulo_rad * (180.0 / math.pi)
        
        # C. Normalizar al rango -1.0 a 1.0 (Centro = 0.0)
        valor_crudo = (angulo_grados / MAX_INCLINACION_GRADOS)*-1
        
        # D. Limitar para que nunca baje de -1.0 ni suba de 1.0
        valor_normalizado = max(-1.0, min(1.0, valor_crudo))
        
        # E. Enviar por MQTT
        payload = ujson.dumps({"inclinacion": valor_normalizado})
        cliente_mqtt.publish(MQTT_TOPIC, payload)
        
        print(f"Ángulo: {angulo_grados:>6.1f}° | Enviado: {valor_normalizado:.3f}")
            
    except OSError as e:
        print("Error de conexión MQTT/WiFi, intentando reconectar...", e)
        time.sleep(2)
        try:
            cliente_mqtt.connect()
        except:
            pass
            
    except Exception as e:
        print("Error en la lectura del sensor:", e)
        
    time.sleep(0.05)