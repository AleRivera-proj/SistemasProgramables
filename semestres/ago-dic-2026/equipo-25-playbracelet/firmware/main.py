import network
import time
import math
import ujson
import socket
from machine import Pin, I2C, ADC
from MPU6050 import MPU6050

# --- 1. CONFIGURACIÓN DE RED Y UDP ---
SSID = "Moka&GizmoHouse"
PASSWORD = "jasaso05"
PC_IP = "192.168.68.118"
PC_PORT = 6510

# --- 2. CALIBRACIÓN DEL GIROSCOPIO ---
MAX_INCLINACION_GRADOS = 65.0
ZONA_MUERTA_GRADOS = 4.0

# --- 3. CALIBRACIÓN DEL SENSOR FLEX (Tu configuración) ---
VALOR_PLANO = 150
VALOR_DOBLADO = 800
SUAVIZADO = 0.15

# --- 4. INICIALIZACIÓN DE HARDWARE ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
mpu = MPU6050(i2c)

sensor_flex = ADC(Pin(32))
sensor_flex.atten(ADC.ATTN_11DB)
sensor_flex.width(ADC.WIDTH_12BIT)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nWiFi conectado. IP:", wlan.ifconfig()[0])

def leer_angulo():
    acel = mpu.read_accel_data(g=True)
    return math.atan2(acel["y"], acel["z"]) * (180.0 / math.pi)

def calibrar_centro(muestras=30):
    print("Mantén el brazo en posición neutra (centro)...")
    suma = 0.0
    for _ in range(muestras):
        suma += leer_angulo()
        time.sleep(0.02)
    centro = suma / muestras
    print(f"Centro calibrado en: {centro:.1f}°")
    return centro

# --- ARRANQUE ---
conectar_wifi()
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

angulo_cero = calibrar_centro()
lectura_suavizada = sensor_flex.read()

# --- BUCLE PRINCIPAL (20 FPS) ---
while True:
    try:
        # A. Calcular inclinación (-1.0 a 0.0 y 0.0 a 1.0)
        angulo_actual = leer_angulo()
        delta_angulo = (angulo_actual - angulo_cero + 180.0) % 360.0 - 180.0

        if abs(delta_angulo) < ZONA_MUERTA_GRADOS:
            inclinacion = 0.0
        else:
            inclinacion = delta_angulo / MAX_INCLINACION_GRADOS
            inclinacion = max(-1.0, min(1.0, inclinacion))

        # B. Leer y normalizar sensor flex (0.0 a 100.0)
        lectura_actual = sensor_flex.read()
        lectura_suavizada = (SUAVIZADO * lectura_actual) + ((1.0 - SUAVIZADO) * lectura_suavizada)

        flexion = (lectura_suavizada - VALOR_PLANO) / (VALOR_DOBLADO - VALOR_PLANO)
        flexion_normalizada = max(0.0, min(1.0, flexion)) * 100

        # C. Enviar paquete JSON a GameMaker
        payload = ujson.dumps({
            "inclinacion": round(inclinacion, 3),
            "flex1": round(flexion_normalizada, 3)
        })
        udp_socket.sendto(payload.encode("utf-8"), (PC_IP, PC_PORT))

        print(f"Inclinación: {inclinacion:>6.3f} | Flex Crudo: {lectura_actual:4d} | Flex Final: {flexion_normalizada:.3f}")

    except Exception as e:
        print("Error en el bucle:", e)
        if not network.WLAN(network.STA_IF).isconnected():
            conectar_wifi()

    time.sleep(0.05)
