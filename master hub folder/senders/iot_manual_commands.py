import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

DEVICE_ID_IOT = "841FE82C1884"

ACTION_TOPIC = f"home/{DEVICE_ID_IOT}/actions"
ACK_TOPIC = f"home/{DEVICE_ID_IOT}/ack"
STATUS_TOPIC = f"home/{DEVICE_ID_IOT}/device/status"


# ======================================
# MQTT CALLBACKS
# ======================================
def on_connect(client, userdata, flags, rc):
    print("MQTT CONNECTED:", rc)

    client.subscribe(ACK_TOPIC)
    client.subscribe(STATUS_TOPIC)

    print("SUBSCRIBED:")
    print(ACK_TOPIC)
    print(STATUS_TOPIC)


def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    print("\nMQTT RECEIVED")
    print("TOPIC   :", msg.topic)
    print("MESSAGE :", payload)


# ======================================
# MQTT CLIENT
# ======================================
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.loop_start()


# ======================================
# COMMAND LIST
# ======================================
commands = [
    "LIGHT_ON",
    "LIGHT_OFF",
    "FAN_ON",
    "FAN_OFF",
    "PUMP_ON",
    "PUMP_OFF",
    "STOP"
]


# ======================================
# MENU
# ======================================
print("\nMANUAL MQTT CONTROL")
print("Commands:")
print("LIGHT_ON")
print("LIGHT_OFF")
print("FAN_ON")
print("FAN_OFF")
print("PUMP_ON")
print("PUMP_OFF")
print("STOP")
print("AUTO_TEST")
print("EXIT")


# ======================================
# MAIN LOOP
# ======================================
while True:

    cmd = input("\nEnter command: ").strip().upper()

    if cmd == "EXIT":
        break

    elif cmd == "AUTO_TEST":

        try:
            delay_sec = int(input("Enter delay in seconds: "))
        except:
            delay_sec = 2

        print("\nStarting Auto Test...\n")

        for c in commands:

            result = client.publish(ACTION_TOPIC, c)

            if result.rc == 0:
                print("SENT ->", c)
            else:
                print("FAILED ->", c)

            time.sleep(delay_sec)

        print("\nAuto Test Completed")

    else:

        result = client.publish(ACTION_TOPIC, cmd)

        if result.rc == 0:
            print("SENT ->", cmd)
        else:
            print("SEND FAILED")

    time.sleep(0.2)


client.loop_stop()
client.disconnect()

print("MQTT Disconnected")