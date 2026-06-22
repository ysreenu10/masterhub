# BROKER = "broker.hivemq.com"
# PORT = 1883
BROKER = "broker.hivemq.com"
PORT = 8883

DEVICE_ID_IOT = "004B12308100"
DEVICE_ID_ROBO = "98A316BF2CC0"

STATUS_TOPICS = [
    f"home/{DEVICE_ID_IOT}/device/status",
    f"home/{DEVICE_ID_IOT}/ack",

    f"ES/{DEVICE_ID_ROBO}/CAR/STATUS",
    f"ES/{DEVICE_ID_ROBO}/CAR/ACK"
]

# MOBILE ADB CONFIG
ADB_PATH = r"C:\Users\91917\Downloads\master hub folder\master hub folder\senders\mobile_sender\bin\adb\adb.exe"

ADB_DEVICE_ID = None

COMMAND_DELAY = 1
LOG_FILE = "logs.txt"