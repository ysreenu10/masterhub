import websocket
import json
import ssl
import time
import threading
from config import CLIENT_ID, CLIENT_SECRET

class CortexClient:
    def __init__(self, command_callback, log_callback=None):
        self.ws_url = "wss://localhost:6868"
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.command_callback = command_callback # Function(command, confidence)
        self.log_callback = log_callback # Function(message)
        self.token = None
        self.session_id = None
        self.ws = None
        self.is_connected = False
        self.stop_event = threading.Event()

    def log(self, message):
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def on_message(self, ws, message):
        data = json.loads(message)
        
        # Handle authentication and session creation responses
        if 'id' in data:
            if 'error' in data:
                self.log(f"Cortex API Error: {data['error']['message']}")
                # If access is not granted, we might need to tell the user to check Emotiv Launcher
                if data['error'].get('code') == -32102:
                    self.log("ACTION REQUIRED: Please open Emotiv Launcher and approve this application.")
                return

            req_id = data['id']
            if req_id == 0: # requestAccess response
                if 'result' in data and data['result'].get('accessGranted'):
                    self.log("Access granted. Authorizing...")
                    self.authorize()
                else:
                    self.log("Access pending. Please approve in Emotiv Launcher.")
            elif req_id == 1: # Authorize response
                self.token = data['result']['cortexToken']
                self.query_headsets()
            elif req_id == 2: # Query headsets response
                if data['result']:
                    headset_id = data['result'][0]['id']
                    self.create_session(headset_id)
                else:
                    self.log("No headset found. Please check your Emotiv App.")
            elif req_id == 3: # Create session response
                self.session_id = data['result']['id']
                self.subscribe()

        # Handle streaming data
        if 'com' in data:
            command = data['com'][0]
            confidence = data['com'][1]
            self.command_callback(command, confidence)

    def on_error(self, ws, error):
        self.log(f"WebSocket Error: {error}")
        self.is_connected = False

    def on_close(self, ws, close_status_code, close_msg):
        self.log("WebSocket Connection Closed")
        self.is_connected = False

    def on_open(self, ws):
        self.log("WebSocket Connection Opened")
        self.is_connected = True
        self.request_access()

    def request_access(self):
        request = {
            "jsonrpc": "2.0",
            "method": "requestAccess",
            "params": {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            },
            "id": 0
        }
        self.ws.send(json.dumps(request))

    def authorize(self):
        auth_request = {
            "jsonrpc": "2.0",
            "method": "authorize",
            "params": {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            },
            "id": 1
        }
        self.ws.send(json.dumps(auth_request))

    def query_headsets(self):
        query_request = {
            "jsonrpc": "2.0",
            "method": "queryHeadsets",
            "id": 2
        }
        self.ws.send(json.dumps(query_request))

    def create_session(self, headset_id):
        session_request = {
            "jsonrpc": "2.0",
            "method": "createSession",
            "params": {
                "cortexToken": self.token,
                "headset": headset_id,
                "status": "active"
            },
            "id": 3
        }
        self.ws.send(json.dumps(session_request))

    def subscribe(self):
        subscribe_request = {
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken": self.token,
                "session": self.session_id,
                "streams": ["com"]
            },
            "id": 4
        }
        self.ws.send(json.dumps(subscribe_request))
        self.log("Subscribed to command and facial streams.")

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Emotiv usually uses self-signed certs for localhost
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def stop(self):
        if self.ws:
            self.ws.close()
        self.stop_event.set()

if __name__ == "__main__":
    def dummy_callback(cmd, conf):
        print(f"Detected: {cmd} ({conf})")
    
    client = CortexClient(dummy_callback)
    client.start()
