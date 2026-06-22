import time
import paho.mqtt.client as mqtt
from config import BROKER, PORT, STATUS_TOPICS, DEVICE_ID_IOT, DEVICE_ID_ROBO
import ssl

print("🌐 MQTT MANAGER LOADED")


def on_connect(client, userdata, flags, rc):
    print("✅ MQTT Connected:", rc)

    for topic in STATUS_TOPICS:
        client.subscribe(topic)
        print("📡 Subscribed:", topic)


def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    # IOT DEVICE STATUS
    if msg.topic == f"home/{DEVICE_ID_IOT}/device/status":
        if payload == "ONLINE":
            print("🏠📡 IOT ESP32 CONNECTED ONLINE-------------------------->")
        elif payload == "OFFLINE":
            print("🏠📴 IOT ESP32 OFFLINE -------------------------->")
        else:
            print("🏠 ℹ️ IOT STATUS:", payload)

    # IOT ACK
    elif msg.topic == f"home/{DEVICE_ID_IOT}/ack":
        print("🏠📨 IOT ACK:", payload)

    # ROBO STATUS
    elif msg.topic == f"ES/{DEVICE_ID_ROBO}/CAR/STATUS":
        if payload == "ONLINE":
            print("🤖📡 ROBO ESP32 CONNECTED ONLINE-------------------------->")
        elif payload == "OFFLINE":
            print("🤖📴 ROBO ESP32 OFFLINE -------------------------->")
        else:
            print("🤖 ℹ️ ROBO STATUS:", payload)

    # ROBO ACK
    elif msg.topic == f"ES/{DEVICE_ID_ROBO}/CAR/ACK":
        print("🤖📨 ROBO ACK:", payload)

    else:
        print(f"📨 MQTT STATUS -> {msg.topic} : {payload}")


# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
# client.on_connect = on_connect
# client.on_message = on_message

# print("🔄 Connecting to MQTT broker...")
# client.connect(BROKER, PORT, 60)

# client.loop_start()

# time.sleep(2)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

client.on_connect = on_connect
client.on_message = on_message

client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

print("🔄 Connecting securely to MQTT broker...")
client.connect("broker.hivemq.com", 8883, 60)

client.loop_start()