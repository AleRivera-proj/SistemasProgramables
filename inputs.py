import network
import time
import math
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C
# Importamos la clase de la librería que me enviaste
from MPU6050 import MPU6050 

i2c = I2C(0, scl=Pin(22), sda=Pin(21),freq=400000)
mpu = MPU6050(i2c)

# --- 1. CONFIGURACIÓN DE RED ---
SSID = "Moka&GizmoHouse"
PASSWORD = "jasaso05"

# --- 2. CONFIGURACIÓN MQTT (Broker Mosquitto) ---
MQTT_BROKER = "192.168.68.119" # IP local de la PC donde corre Mosquitto
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
        # A. Obtener datos de aceleración de tu librería.
        # Usamos g=True para obtener los valores en fuerzas G, que son más fáciles de procesar.
        aceleracion = mpu.read_accel_data(g=True)
        
        # Tu librería devuelve un diccionario, así que extraemos los valores así:
        ax = aceleracion["x"]
        ay = aceleracion["y"]
        az = aceleracion["z"]
        
        # B. Calcular la magnitud del vector de gravedad
        magnitud = math.sqrt(ax**2 + ay**2 + az**2)
        
        if magnitud > 0:
            # C. Calcular ángulo respecto a la vertical (Asumiendo que el eje Y apunta arriba/abajo)
            rad = math.acos(abs(ay) / magnitud)
            angulo_grados = rad * (180.0 / math.pi)
            
            # D. Normalizar y limitar entre 0 y 1
            valor_normalizado = max(0.0, min(1.0, angulo_grados / MAX_INCLINACION_GRADOS))
            
            # E. Preparar el mensaje (JSON como cadena de texto)
            payload = ujson.dumps({"inclinacion": valor_normalizado})
            
            # F. Publicar por MQTT
            cliente_mqtt.publish(MQTT_TOPIC, payload)
            
            print(f"Ángulo: {angulo_grados:.1f}° -> Enviado: {payload}")
            
    except OSError as e:
        print("Error de conexión MQTT/WiFi, intentando reconectar...", e)
        time.sleep(2)
        try:
            cliente_mqtt.connect() # Intenta reconectar al broker si se cae
        except:
            pass
            
    except Exception as e:
        print("Error en la lectura del sensor:", e)
        
    # Pausa de 50ms para no saturar, pero lo suficientemente rápido para un juego (20 FPS)
    time.sleep(0.05)