from mqtt_manager import client
from config import DEVICE_ID_ROBO

print("🤖 EMBEDDED SENDER MODULE LOADED")


def send_embedded_command(action):
    command_map = {
        "ROBO_FORWARD": "FORWARD",
        "ROBO_BACKWARD": "BACKWARD",
        "ROBO_LEFT": "LEFT",
        "ROBO_RIGHT": "RIGHT",
        "ROBO_STOP": "STOP"
    }

    payload = command_map.get(action)

    if payload:
        topic = f"ES/{DEVICE_ID_ROBO}/CAR/ACTIONS"

        result = client.publish(topic, payload)

        if result.rc == 0:
            print(f"🤖✅ MQTT SENT -> {topic} : {payload}")
        else:
            print(f"🤖❌ MQTT SEND FAILED -> {topic}")