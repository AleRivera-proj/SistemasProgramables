const mqtt = require('mqtt');
const dgram = require('dgram');

// Configuración de Mosquitto (Broker)
const opciones = {
    username: 'admin',
    password: 'MiClave2026'
};
const MQTT_BROKER = 'mqtt://localhost'; // Si Mosquitto está en esta misma PC
const MQTT_TOPIC = 'juego/controles/';

// Configuración de GameMaker (UDP)
const GM_HOST = '127.0.0.1';
const GM_PORT = 6510; // El puerto que GameMaker estará escuchando

// Iniciar clientes
const mqttClient = mqtt.connect(MQTT_BROKER, opciones);
const udpClient = dgram.createSocket('udp4');

// Cuando se conecta a Mosquitto
mqttClient.on('connect', () => {
    console.log('Conectado a Mosquitto MQTT broker');
    mqttClient.subscribe(MQTT_TOPIC, (err) => {
        if (!err) {
            console.log(`Suscrito al topic: ${MQTT_TOPIC}`);
        } else {
            console.error('Error al suscribirse:', err);
        }
    });
});

// Cuando llega un mensaje desde el ESP32
mqttClient.on('message', (topic, message) => {
    const datoString = message.toString();
    console.log(`Mensaje recibido de ESP32 [${topic}]: ${datoString}`);

    // Reenviar a GameMaker vía UDP
    const buffer = Buffer.from(datoString);
    udpClient.send(buffer, 0, buffer.length, GM_PORT, GM_HOST, (err) => {
        if (err) {
            console.error('Error enviando UDP a GameMaker:', err);
        } else {
            console.log(`-> Reenviado a GameMaker (${GM_HOST}:${GM_PORT})`);
        }
    });
});

// Mostrar errores de conexión para saber por qué se cierra
mqttClient.on('error', (err) => {
    console.error('Error en MQTT:', err.message);
});

// Evitar que el programa colapse por errores inesperados
process.on('uncaughtException', (err) => {
    console.error('Error crítico:', err);
});