import json
import time

from state_manager import *
from logger import save_log
from command_parser import parse_command

from senders.embedded_sender import send_embedded_command
from senders.iot_sender import send_iot_command
from senders.desktop_sender import send_desktop_command
# from senders.mobile_sender.mobile_sender import send_mobile_command
#from senders.jiosaavn_desktop_sender.music_controller import MusicController
from senders.jiosaavn_mobile_sender.music_controller import MusicController
from config import COMMAND_DELAY


with open("command.json", "r") as file:
    events = json.load(file)

print("✅ MASTER HUB STARTED")

# Initialize the JioSaavn music controller for PC/Mobile
try:
    print("🧠 INITIALIZING JIOSAAVN CONTROLLER...")
    jiosaavn_controller = MusicController()
except Exception as e:
    print(f"⚠️ JioSaavn Controller not fully initialized: {e}")
    jiosaavn_controller = None


def emergency_stop():
    print("🛑 GLOBAL EMERGENCY STOP")

    send_iot_command("STOP")
    send_embedded_command("ROBO_STOP")
    send_desktop_command("STOP")
    if jiosaavn_controller:
        # Pause/Stop JioSaavn
        #jiosaavn_controller.trigger_action("RIGHT_PLAYPAUSE")
         jiosaavn_controller.trigger_action("PLAY/PAUSE")
    else:
        send_mobile_command("PLAYPAUSE")

for event in events:

    command = event["output_to_hub"]["final_command"].strip()

    print("\n------------------")
    print("📨 Command:", command)

    state = get_state()

    domain, action = parse_command(command)

    if not domain:
        print("❌ INVALID COMMAND FORMAT")
        continue

    # GLOBAL STOP
    if domain == "GLOBAL":
        emergency_stop()
        reset()
        time.sleep(COMMAND_DELAY)
        continue

    # DEVICE SELECTION
    if state == "DEVICE_SELECTION":

        if domain == "SELECT":
            set_domain(action)
            set_state("DEVICE_CONTROL")

            domain_icons = {
                "IOT": "🏠",
                "EMBEDDED": "🤖",
                "DESKTOP": "🖥️",
                "MOBILE": "📱"
            }

            print(f"🎯 DOMAIN SELECTED: {domain_icons.get(action, '🔄')} {action}")

            save_log(f"DOMAIN SELECTED -> {action}")

        else:
            print("⚠️ WAITING FOR DOMAIN SELECTION")

        continue

    # DEVICE CONTROL
    if state == "DEVICE_CONTROL":

        current_domain = get_domain()

        if domain != current_domain:
            print("🚫 INVALID DOMAIN COMMAND")
            continue

        print("🌍 Domain:", current_domain)
        print("⚙️ Action:", action)

        save_log(
            f"Domain: {current_domain} | "
            f"Command: {command} | "
            f"Action: {action}"
        )

        if current_domain == "IOT":

            print("🏠 Sending IOT command...")
            send_iot_command(action)

        elif current_domain == "EMBEDDED":

            print("🤖 Sending ROBO command...")
            send_embedded_command(action)

        elif current_domain == "DESKTOP":

            print("🖥️ Sending Desktop command...")
            send_desktop_command(action)

        elif current_domain == "MOBILE":

            print("📱 Sending JioSaavn command...")

            if jiosaavn_controller:

                print(f"\n🚀 EXECUTING ACTION: {action}")

                success = jiosaavn_controller.trigger_action(action)

                print(f"🎯 FINAL RESULT: {success}")

                if success:
                    print(f"✅ Action '{action}' executed successfully by JioSaavn Controller!")
                else:
                    print(f"⚠️ Action '{action}' was skipped or failed.")

            else:

                print("⚠️ JioSaavn Controller is None")
                send_mobile_command(action)

        time.sleep(COMMAND_DELAY)

print("\n✅ PROCESS FINISHED")

