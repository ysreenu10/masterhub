
import webbrowser
import pyautogui
import pygetwindow as gw
import time


class MusicController:

    # ==========================
    # JIOSAAVN COORDINATES
    # ==========================

    SEARCH_X = 902
    SEARCH_Y = 173

    PLAY_X = 942
    PLAY_Y = 1013

    NEXT_X = 1023
    NEXT_Y = 1017

    PREV_X = 874
    PREV_Y = 1014

    def __init__(self):

        print("🎵 JioSaavn Controller Ready")

        self.demo_songs = [
            "NTR Songs",
            "Allu Arjun Songs",
            "Pawan Kalyan Songs",
            "Prabhas Songs",
            "Mahesh Babu Songs",
            "Ram Charan Songs",
            "Devara Songs",
            "Pushpa Songs",
            "Salaar Songs",
            "OG Songs"
        ]

        self.song_index = 0

    # ==========================
    # FIND / FOCUS JIOSAAVN
    # ==========================

    def focus_jiosaavn(self):

        try:

            for title in gw.getAllTitles():

                if "JioSaavn" in title:

                    print("✅ JioSaavn Found")

                    window = gw.getWindowsWithTitle(title)[0]

                    try:
                        window.activate()
                    except:
                        pass

                    time.sleep(1)

                    return True

        except Exception as e:

            print("Focus Error:", e)

        return False

    # ==========================
    # OPEN JIOSAAVN
    # ==========================

    def open_jiosaavn(self):

        if self.focus_jiosaavn():

            print("✅ Using Existing JioSaavn Window")

            return True

        print("🌐 Opening JioSaavn")

        webbrowser.open("https://www.jiosaavn.com")

        time.sleep(8)

        return True

    # ==========================
    # SEARCH SONG
    # ==========================

    def search_song(self, song_name):

        self.open_jiosaavn()

        print(f"🔍 Searching: {song_name}")

        pyautogui.click(self.SEARCH_X, self.SEARCH_Y)

        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "a")

        pyautogui.press("backspace")

        pyautogui.write(song_name, interval=0.03)

        time.sleep(0.5)

        pyautogui.press("enter")

        return True

    # ==========================
    # RANDOM SEARCH DEMO
    # ==========================

    def search_random_song(self):

        song = self.demo_songs[self.song_index]

        self.song_index += 1

        if self.song_index >= len(self.demo_songs):
            self.song_index = 0

        return self.search_song(song)

    # ==========================
    # PLAY / PAUSE
    # ==========================

    def play_pause(self):

        self.open_jiosaavn()

        pyautogui.click(
            self.PLAY_X,
            self.PLAY_Y
        )

        return True

    # ==========================
    # NEXT TRACK
    # ==========================

    def next_track(self):

        self.open_jiosaavn()

        pyautogui.click(
            self.NEXT_X,
            self.NEXT_Y
        )

        return True

    # ==========================
    # PREVIOUS TRACK
    # ==========================

    def prev_track(self):

        self.open_jiosaavn()

        print("⏮️ PREVIOUS TRACK")

        # First click restarts song
        pyautogui.click(
            self.PREV_X,
            self.PREV_Y
        )

        time.sleep(0.7)   # adjust if needed

        # Second click goes to previous song
        pyautogui.click(
            self.PREV_X,
            self.PREV_Y
        )

        return True

    # ==========================
    # VOLUME UP
    # ==========================

    def volume_up(self):

        pyautogui.press("volumeup")

        return True

    # ==========================
    # VOLUME DOWN
    # ==========================

    def volume_down(self):

        pyautogui.press("volumedown")

        return True

    # ==========================
    # MUTE
    # ==========================

    def mute(self):

        pyautogui.press("volumemute")
        return True

        return True

    # ==========================
    # MASTER ROUTER
    # ==========================

    def trigger_action(self, action):

        action = action.upper()

        print(f"\n🎵 MUSIC ACTION -> {action}")

        try:

            if "HOME" in action:

                return self.open_jiosaavn()

            elif "PLAYPAUSE" in action:

                return self.play_pause()

            elif "NEXTTRACK" in action:

                return self.next_track()

            elif "PREVTRACK" in action:

                return self.prev_track()

            elif "VOLUMEUP" in action:

                return self.volume_up()

            elif "VOLUMEDOWN" in action:

                return self.volume_down()

            elif "MUTE" in action:

                return self.mute()

            elif "SEARCH" in action:

                return self.search_random_song()

            else:

                print("⚠️ Unknown Action")

                return False

        except Exception as e:

            print("❌ Music Controller Error:", e)

            return False