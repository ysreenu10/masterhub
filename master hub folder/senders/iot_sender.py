from mqtt_manager import client
from config import DEVICE_ID_IOT

print("🏠 IOT SENDER MODULE LOADED")


def send_iot_command(action):
    topic = f"home/{DEVICE_ID_IOT}/actions"

    result = client.publish(topic, action)

    if result.rc == 0:
        print(f"🏠✅ MQTT SENT -> {topic} : {action}")
    else:
        print(f"🏠❌ MQTT SEND FAILED -> {topic}")
        