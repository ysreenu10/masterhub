import paho.mqtt.client as mqtt
import json
import time
import sys
import random

BROKER_URL = "broker.emqx.io"
PORT = 8084
TOPIC = "bci/music/commands"

class MqttInfiniteRunner:
    def __init__(self):
        # Using Callback API Version 2 or 1 compatible client initialization with websockets
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        except AttributeError:
            self.client = mqtt.Client(transport="websockets")
        self.is_connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        # Handle both v1 and v2 callback signature differences safely
        code = rc if isinstance(rc, int) else rc.value
        if code == 0:
            print("\n[MQTT SUCCESS] Connected securely via SSL WebSocket to 'broker.emqx.io' successfully!")
            self.is_connected = True
        else:
            print(f"\n[MQTT ERROR] Connection failed with code: {code}")
            self.is_connected = False

    def on_disconnect(self, client, userdata, disconnect_flags, rc=None, properties=None):
        print("\n[MQTT] Connection lost. Reconnecting...")
        self.is_connected = False

    def connect(self):
        print(f"[MQTT] Connecting securely via SSL WebSocket to public IoT broker: {BROKER_URL}:{PORT}...")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        try:
            self.client.tls_set() # Enables standard secure SSL/TLS encryption!
            self.client.ws_set_options(path="/mqtt") # Standard WebSocket path for EMQX
            self.client.connect(BROKER_URL, PORT, 60)
            self.client.loop_start() # Keeps connection alive in a background thread!
            return True
        except Exception as e:
            print(f"[MQTT ERROR] Connection failed: {e}")
            self.is_connected = False
            return False

    def publish_command(self, action, query=""):
        if not self.is_connected:
            print("[MQTT WARNING] Client not connected. Command buffered.")
            return False

        payload = {
            "action": action,
            "query": query
        }
        
        try:
            message = json.dumps(payload)
            self.client.publish(TOPIC, message)
            print(f"[MQTT SUCCESS] Broadcasted: {payload} on topic '{TOPIC}'")
            return True
        except Exception as e:
            print(f"[MQTT ERROR] Failed to send: {e}")
            return False

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Disconnected safely.")

if __name__ == "__main__":
    print("=============================================================")
    print("     BCI MQTT INFINITE TEST LOOP FOR MOBILE AND PC           ")
    print("=============================================================")
    print(f"Connecting to broker: {BROKER_URL}")
    print(f"Subscribed Topic on Mobile: {TOPIC}")
    print("This script will stay connected and publish commands every 3s.")
    print("Press Ctrl+C at any time to exit.")
    print("=============================================================\n")

    runner = MqttInfiniteRunner()
    if runner.connect():
        # Allow connection to establish
        time.sleep(2.0)
        
        search_terms = [
            "Telugu Popular Songs",
            "Pawan Kalyan Hits",
            "Bahubali Songs",
            "Allu Arjun Songs",
            "Mahesh Babu Hits",
            "NTR Songs",
            "Anirudh Songs"
        ]
        
        commands = [
            ("play/pause", ""),
            ("volumeup", ""),
            ("volumeup", ""),
            ("volumedown", ""),
            ("nexttrack", ""),
            ("prevtrack", ""),
            ("home", ""),
            ("search", "Allu Arjun Songs") # Triggers dynamic search deep-links!
        ]
        
        counter = 1
        try:
            while True:
                # Cycle through standard BCI music commands
                action, query = commands[(counter - 1) % len(commands)]
                
                # Pick a random search query if it is a search action
                if action == "search":
                    query = random.choice(search_terms)
                
                print(f"\n[Command #{counter}] Dispatching BCI Action...")
                runner.publish_command(action, query)
                
                print("Waiting 4.0 seconds (connection stays active)...")
                time.sleep(4.0) # Increased slightly to let JioSaavn deep-link pages load cleanly!
                counter += 1
        except KeyboardInterrupt:
            print("\nStopping BCI Infinite Loop...")
        finally:
            runner.close()
            print("Finished.")
