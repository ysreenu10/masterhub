import webbrowser
import pyautogui
import time

# ==========================
# COORDINATES
# ==========================

SEARCH_X = 902
SEARCH_Y = 173

PLAY_X = 942
PLAY_Y = 1013

NEXT_X = 1023
NEXT_Y = 1017

PREV_X = 874
PREV_Y = 1014

# ==========================
# OPEN JIOSAAVN
# ==========================

print("Opening JioSaavn...")
webbrowser.open("https://www.jiosaavn.com")

print("Waiting for page load...")
time.sleep(10)

# ==========================
# SEARCH SONG
# ==========================

print("Searching Believer...")

pyautogui.click(SEARCH_X, SEARCH_Y)

time.sleep(1)

pyautogui.hotkey("ctrl", "a")
pyautogui.press("backspace")

pyautogui.write("Believer", interval=0.05)

time.sleep(1)

pyautogui.press("enter")

time.sleep(5)

# ==========================
# LOOP CONTROLS
# ==========================

while True:

    print("PLAY / PAUSE")
    pyautogui.click(PLAY_X, PLAY_Y)
    time.sleep(3)

    print("PLAY / PAUSE")
    pyautogui.click(PLAY_X, PLAY_Y)
    time.sleep(3)

    print("NEXT TRACK")
    pyautogui.click(NEXT_X, NEXT_Y)
    time.sleep(3)

    print("PREVIOUS TRACK")
    pyautogui.click(PREV_X, PREV_Y)
    time.sleep(3)

    print("VOLUME UP")
    pyautogui.press("volumeup")
    time.sleep(3)

    print("VOLUME DOWN")
    pyautogui.press("volumedown")
    time.sleep(3)