import keyboard
import random
import time
import webbrowser
import subprocess
import urllib.parse
from urllib.parse import quote_plus

from . import mobile_config

from .mobile_config import (
    DEBOUNCE_TIME,
    JIOSAAVN_URL,
    NEW_RELEASES_URL,
    AUTO_PLAY_FIRST_SONG,
    JIOSAAVN_OPEN_WAIT_SECONDS,
    SEARCH_TERMS
)


# import mobile_config
# from mobile_config import DEBOUNCE_TIME, JIOSAAVN_URL, NEW_RELEASES_URL, AUTO_PLAY_FIRST_SONG, JIOSAAVN_OPEN_WAIT_SECONDS, SEARCH_TERMS
# import adb_helper
# from config import COMMAND_MAP, DEBOUNCE_TIME, JIOSAAVN_URL, NEW_RELEASES_URL, AUTO_PLAY_FIRST_SONG, JIOSAAVN_OPEN_WAIT_SECONDS, SEARCH_TERMS

class MusicController:
    def __init__(self, log_callback=print):
        self.log_fn = log_callback
        self.last_trigger_time = 0
        self.debounce_interval = DEBOUNCE_TIME
        self.search_terms = SEARCH_TERMS

        # Map internal action names to keyboard library media keys (PC mode)
        self.key_map = {
            "play/pause": "play/pause media",
            "prevtrack": "previous track",
            "nexttrack": "next track",
            "volumeup": "volume up",
            "volumedown": "volume down"
        }
        self.special_action_handlers = {
            "home": self.go_home,
            "search": self.search_jiosaavn
        }

        # Check target: PC or Mobile
        self.target = getattr(mobile_config, "CONTROL_TARGET", "pc").lower()
        
        if self.target == "mobile":
            self.log_fn("Music Controller: Target set to MOBILE (Wireless MQTT SSL WebSockets)")
            self.mqtt_topic = "bci/music/commands"
            
            import paho.mqtt.client as mqtt
            try:
                self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
            except AttributeError:
                self.mqtt_client = mqtt.Client(transport="websockets")
            
            try:
                self.mqtt_client.tls_set() # Enable SSL/TLS encryption
                self.mqtt_client.ws_set_options(path="/mqtt") # WebSocket path for EMQX
                self.mqtt_client.connect("broker.emqx.io", 8084, 60)
                self.mqtt_client.loop_start() # Keeps connection alive in background thread
                self.log_fn("[MQTT SUCCESS] Connected PC BCI publisher to broker.emqx.io:8084 successfully!")
            except Exception as e:
                self.log_fn(f"[MQTT ERROR] Failed to connect PC BCI publisher: {e}")

            # Initialize ADB for automated on-screen input if connected
            self.adb_device_id = getattr(mobile_config, "ADB_DEVICE_ID", None)
            
            # Load last saved device address
            import os
            if not self.adb_device_id:
                try:
                    if os.path.exists(".last_device"):
                        with open(".last_device", "r") as f:
                            saved = f.read().strip()
                            if saved:
                                self.adb_device_id = saved
                                self.log_fn(f"Loaded last saved device: {self.adb_device_id}")
                except Exception:
                    pass

            try:
                from . import adb_helper
                self.adb_path = adb_helper.get_or_download_adb(getattr(mobile_config, "ADB_PATH", "adb"), log_fn=self.log_fn)
                if self.adb_path:
                    # Auto-connect if wireless device
                    if self.adb_device_id and ":" in str(self.adb_device_id):
                        self.log_fn(f"Attempting to auto-connect to {self.adb_device_id}...")
                        subprocess.run([self.adb_path, "connect", self.adb_device_id], capture_output=True, timeout=5)
            except Exception as e:
                self.adb_path = None
                self.log_fn(f"ADB initialization skipped or failed: {e}")
        else:
            self.log_fn("Music Controller: Target set to PC (Web Browser)")
            # Check if JioSaavn is already open in the browser to avoid opening multiple tabs
            hwnd = self.find_jiosaavn_hwnd()
            if hwnd:
                self.log_fn("JioSaavn window already open. Focusing existing tab to avoid opening multiple tabs.")
                self.focus_jiosaavn()
            else:
                self.log_fn(f"Opening JioSaavn New Releases: {NEW_RELEASES_URL}")
                webbrowser.open(NEW_RELEASES_URL)

            if AUTO_PLAY_FIRST_SONG:
                self.start_jiosaavn_playback()

    # ==================== MOBILE MQTT CONTROL IMPLEMENTATION ====================

    def run_adb(self, args):
        """Execute an ADB command with the initialized ADB path and device ID."""
        if not hasattr(self, "adb_path") or not self.adb_path:
            return False
        
        cmd = [self.adb_path]
        if hasattr(self, "adb_device_id") and self.adb_device_id:
            cmd += ["-s", self.adb_device_id]
        cmd += args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            self.log_fn(f"ADB execution exception: {e}")
            return False

    def get_mobile_screen_size(self):
        try:
            result = subprocess.run([self.adb_path, "shell", "wm", "size"], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                line = result.stdout.strip()
                size_str = line.split(":")[-1].strip()
                w, h = map(int, size_str.split("x"))
                return w, h
        except Exception:
            pass
        return 1080, 2400  # Default fallback

    def trigger_mobile_action(self, action, command):
        """Publish BCI commands securely via MQTT WebSockets to the phone APK."""
        import json
        
        payload = {
            "action": action,
            "query": ""
        }
        
        query = ""
        if action == "search":
            query = random.choice(self.search_terms)
            payload["query"] = quote_plus(query)
            self.log_fn(f"[MQTT BCI] Selected BCI search query: '{query}'")
        
        try:
            message = json.dumps(payload)
            self.mqtt_client.publish(self.mqtt_topic, message)
            self.log_fn(f"[MQTT BCI SUCCESS] Published action: '{action}' over the cloud to your phone!")
        except Exception as e:
            self.log_fn(f"[MQTT BCI ERROR] Failed to publish BCI command: {e}")

        # If it is a search action, also try to perform ADB typing/clicking if a phone is connected
        if action == "search" and query:
            try:
                from . import adb_helper
                devices = adb_helper.get_connected_devices(self.adb_path)
                if devices:
                    if not self.adb_device_id or self.adb_device_id not in devices:
                        self.adb_device_id = devices[0]
                    
                    self.log_fn(f"Automating search on phone {self.adb_device_id} via ADB...")
                    
                    # 1. Wake up screen and dismiss keyguard
                    self.run_adb(["shell", "input", "keyevent", "224"])
                    self.run_adb(["shell", "wm", "dismiss-keyguard"])
                    self.run_adb(["shell", "input", "keyevent", "82"])
                    
                    # 2. Get screen size to dynamically calculate coordinates
                    w, h = self.get_mobile_screen_size()
                    
                    # Base layout coordinates ratios
                    # Search Tab (bottom center-left): x_ratio = 0.30, y_ratio = 0.92
                    # Search Box (top center): x_ratio = 0.50, y_ratio = 0.075
                    search_tab_x = str(int(w * 0.30))
                    search_tab_y = str(int(h * 0.92))
                    search_box_x = str(int(w * 0.50))
                    search_box_y = str(int(h * 0.075))
                    
                    # 3. Tap the Search navigation tab at the bottom
                    self.run_adb(["shell", "input", "tap", search_tab_x, search_tab_y])
                    time.sleep(1.2)
                    
                    # 4. Tap the Search input box at the top
                    self.run_adb(["shell", "input", "tap", search_box_x, search_box_y])
                    time.sleep(0.6)
                    
                    # 5. Escape query spaces with %s to prevent ADB input text parsing errors
                    formatted_query = query.replace(" ", "%s")
                    self.run_adb(["shell", "input", "text", formatted_query])
                    time.sleep(0.8)
                    
                    # 6. Press enter to submit the search query
                    self.run_adb(["shell", "input", "keyevent", "66"])
                    self.log_fn(f"Mobile ADB: Automatically entered query and submitted search.")
                else:
                    self.log_fn("No ADB device connected. Automated on-screen search typing skipped.")
            except Exception as e:
                self.log_fn(f"ADB automation failed: {e}")

        return query if action == "search" else True

    # ==================== ORIGINAL PC WEB CONTROL IMPLEMENTATION ====================

    def find_jiosaavn_hwnd(self):
        """Return the JioSaavn window handle if one exists."""
        import ctypes
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        target_hwnd = [None]

        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    if "jiosaavn" in buff.value.lower():
                        target_hwnd[0] = hwnd
                        return False
            return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)
        return target_hwnd[0]

    def focus_jiosaavn(self):
        """Focus the JioSaavn window if available."""
        import ctypes
        hwnd = self.find_jiosaavn_hwnd()
        if not hwnd:
            return False
        
        user32 = ctypes.windll.user32
        
        # 1. Un-minimize/Restore if minimized
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            time.sleep(0.15)
        
        # 2. Show the window
        user32.ShowWindow(hwnd, 5) # SW_SHOW
        time.sleep(0.1)
        
        # 3. Bypass Windows focus-stealing restrictions
        # Send a harmless 'alt' key press to the current active window to authorize focus changes
        try:
            import keyboard
            keyboard.send("alt")
            time.sleep(0.08)
        except Exception:
            pass
            
        # 4. Bring the JioSaavn window to the front
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        return True

    def click_jiosaavn_search_icon(self):
        """Click the search icon/bar on the JioSaavn page using client-area coordinates."""
        import ctypes
        from ctypes import wintypes

        hwnd = self.find_jiosaavn_hwnd()
        if not hwnd:
            return False

        user32 = ctypes.windll.user32
        client_rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(client_rect)):
            return False

        top_left = wintypes.POINT(client_rect.left, client_rect.top)
        if not user32.ClientToScreen(hwnd, ctypes.byref(top_left)):
            return False

        client_width = client_rect.right - client_rect.left

        # Get the DPI scaling of the window (default is 96 DPI, which is 100% scaling)
        try:
            dpi = user32.GetDpiForWindow(hwnd)
            scaling_factor = dpi / 96.0
        except Exception:
            scaling_factor = 1.0

        # Base Y coordinate at 100% scale (accounting for bookmarks bar presence/absence)
        # 132px works perfectly as the middle-point under standard layouts.
        base_y_offset = 132
        scaled_y_offset = int(base_y_offset * scaling_factor)

        click_x = top_left.x + int(client_width * 0.5)
        click_y = top_left.y + scaled_y_offset

        orig_pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(orig_pt))
        user32.SetCursorPos(click_x, click_y)
        time.sleep(0.15)

        MOUSEEVENTF_LEFTDOWN = 0x0002
        MOUSEEVENTF_LEFTUP = 0x0004
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)

        user32.SetCursorPos(orig_pt.x, orig_pt.y)
        return True

    def click_jiosaavn_first_track(self):
        """Click the first track card on the JioSaavn New Releases page."""
        import ctypes
        from ctypes import wintypes

        hwnd = self.find_jiosaavn_hwnd()
        if not hwnd:
            return False

        user32 = ctypes.windll.user32
        client_rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(client_rect)):
            return False

        top_left = wintypes.POINT(client_rect.left, client_rect.top)
        if not user32.ClientToScreen(hwnd, ctypes.byref(top_left)):
            return False

        client_width = client_rect.right - client_rect.left
        client_height = client_rect.bottom - client_rect.top

        click_x = top_left.x + int(client_width * 0.45)
        click_y = top_left.y + int(client_height * 0.40)

        orig_pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(orig_pt))
        user32.SetCursorPos(click_x, click_y)
        time.sleep(0.15)

        MOUSEEVENTF_LEFTDOWN = 0x0002
        MOUSEEVENTF_LEFTUP = 0x0004
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)

        user32.SetCursorPos(orig_pt.x, orig_pt.y)
        return True

    def start_jiosaavn_playback(self):
        """
        Focus JioSaavn, open New Releases, and attempt to play the first visible track.
        """
        print("Waiting for JioSaavn New Releases to load before autoplay...")
        time.sleep(JIOSAAVN_OPEN_WAIT_SECONDS)

        if not self.focus_jiosaavn():
            print("Could not find JioSaavn window immediately; retrying...")
            time.sleep(4)
            self.focus_jiosaavn()

        time.sleep(1.0)

        # Navigate to the New Releases page in the same tab if needed.
        keyboard.send("ctrl+l")
        time.sleep(0.2)
        keyboard.write(NEW_RELEASES_URL)
        keyboard.send("enter")
        time.sleep(8.0)

        # Click the first New Releases song card directly.
        if not self.click_jiosaavn_first_track():
            print("Could not click first New Releases track. Falling back to tab navigation.")
            for _ in range(14):
                keyboard.send("tab")
                time.sleep(0.12)
            keyboard.send("enter")

        time.sleep(1.0)
        keyboard.send("space")
        print("New Releases first song playback attempted.")

    # def trigger_action(self, command):
    #     """
    #     Triggers a media key or JioSaavn-specific action based on the command.
    #     """
    #     current_time = time.time()
    #     if current_time - self.last_trigger_time < self.debounce_interval:
    #         return False

    #     action = COMMAND_MAP.get(command.lower())
    #     if not action:
    #         return False

    #     # Route action to appropriate target (Mobile or PC)
    #     if self.target == "mobile":
    #         result = self.trigger_mobile_action(action, command)
    #         if result:
    #             self.last_trigger_time = current_time
    #         return result
        
    #     # Original PC routing logic
    #     if action in self.special_action_handlers:
    #         if not self.focus_jiosaavn():
    #             print("JioSaavn window not found. Cannot perform home/search action.")
    #             return False
    #         result = self.special_action_handlers[action]()
    #         if result:
    #             self.last_trigger_time = current_time
    #         return result

    #     key_to_press = self.key_map.get(action)
    #     if key_to_press:
    #         # Try to target JioSaavn specifically
    #         found = self.focus_jiosaavn()
    #         if not found:
    #             print("JioSaavn window not found. Sending global media key...")
            
    #         print(f"Triggering key: {key_to_press} for command: {command}")
    #         try:
    #             keyboard.send(key_to_press)
    #             self.last_trigger_time = current_time
    #             return True
    #         except Exception as e:
    #             print(f"Error triggering key: {e}")
    #             return False
    #     else:
    #         print(f"No key mapping found for action: {action}")
    #         return False
    def trigger_action(self, command):
        """
        Triggers a media key or JioSaavn-specific action based on the command.
        """
        current_time = time.time()

        if current_time - self.last_trigger_time < self.debounce_interval:
            return False

        action = command.strip().lower()

        # Route action to appropriate target (Mobile or PC)
        if self.target == "mobile":
            result = self.trigger_mobile_action(action, command)

            if result:
                self.last_trigger_time = current_time

            return result

        # Original PC routing logic
        if action in self.special_action_handlers:
            if not self.focus_jiosaavn():
                print("JioSaavn window not found. Cannot perform home/search action.")
                return False

            result = self.special_action_handlers[action]()

            if result:
                self.last_trigger_time = current_time

            return result

        key_to_press = self.key_map.get(action)

        if key_to_press:
            found = self.focus_jiosaavn()

            if not found:
                print("JioSaavn window not found. Sending global media key...")

            print(f"Triggering key: {key_to_press} for command: {command}")

            try:
                keyboard.send(key_to_press)
                self.last_trigger_time = current_time
                return True

            except Exception as e:
                print(f"Error triggering key: {e}")
                return False

        print(f"No key mapping found for action: {action}")
        return False

    def go_home(self):
        """Navigate JioSaavn to the home page in the current browser tab."""
        try:
            keyboard.send("ctrl+l")
            time.sleep(0.2)
            keyboard.write(JIOSAAVN_URL)
            keyboard.send("enter")
            print("Navigated JioSaavn to home page using the current tab.")
            time.sleep(5.0)
            return True
        except Exception as e:
            print(f"Error navigating home: {e}")
            return False

    def search_jiosaavn(self):
        """Perform a JioSaavn search using a random selection from the configured term list."""
        try:
            query = random.choice(self.search_terms)
            self.log_fn(f"Think command selected search term: {query}")

            # Focus JioSaavn window
            if not self.focus_jiosaavn():
                self.log_fn("JioSaavn window not found. Opening search page directly in web browser.")
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.jiosaavn.com/search/{encoded_query}"
                webbrowser.open(search_url)
                time.sleep(4.0)
                return query

            # Click the on-page search bar centered in the header
            if not self.click_jiosaavn_search_icon():
                self.log_fn("Could not click JioSaavn search bar.")
                return False

            time.sleep(0.3)

            # Clear existing text inside the search bar (select all and delete)
            keyboard.send("ctrl+a")
            time.sleep(0.1)
            keyboard.send("backspace")
            time.sleep(0.1)

            # Write the query and press Enter to trigger the search
            keyboard.write(query)
            time.sleep(0.4)  # Increased delay to allow browser and JS suggestion lists to register input
            keyboard.send("enter")
            time.sleep(0.15)
            keyboard.send("enter")  # Double enter to guarantee submission if dropdown swallows the first
            self.log_fn(f"Search activated inside the on-page search box for: {query}")
            time.sleep(5.0)
            return query
        except Exception as e:
            self.log_fn(f"Error performing search: {e}")
            return False

if __name__ == "__main__":
    # Test
    mc = MusicController()
    mc.trigger_action("push")
