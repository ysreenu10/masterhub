import serial
import time

print("DESKTOP SENDER MODULE LOADED")

SERIAL_PORT = "COM11"
BAUD_RATE = 115200

ser = None

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    time.sleep(4)

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print(f"DESKTOP SERIAL CONNECTED -> {SERIAL_PORT}")

except Exception as e:
    print(f"DESKTOP SERIAL NOT AVAILABLE -> {e}")


def send_desktop_command(action):
    global ser

    if not action:
        print("DESKTOP: No action")
        return

    if ser is None:
        print("DESKTOP SERIAL UNAVAILABLE")
        return

    try:
        ser.write((action + "\n").encode())
        print("DESKTOP SERIAL SENT ->", action)

        time.sleep(0.3)

        if ser.in_waiting:
            response = ser.readline().decode(errors="ignore").strip()
            print("ESP32 RESPONSE ->", response)

    except Exception as e:
        print("DESKTOP SERIAL ERROR:", e)

        try:
            ser.close()
        except:
            pass

        ser = None

