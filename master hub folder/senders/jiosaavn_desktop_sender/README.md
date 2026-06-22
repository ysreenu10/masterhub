# 🧠 Controlling JioSaavn Using Brain-Computer Interface (BCI)

Welcome! This system allows you to control the **JioSaavn Music App** on your PC browser or directly on your Android phone using mind commands simulated from a dataset or streamed live from an Emotiv BCI Headset.

---

## ⚡ Double-Click Shortcuts (Easiest Access)

We have created two double-clickable Windows shortcut scripts inside this folder for super-fast access:

1. **`Connect_Phone.bat`** (Easiest):
   * Simply **double-click this file** on your computer.
   * It will ask you: `Enter the PORT number shown on your phone`.
   * Type the port number from your screen and press **Enter**.
   * It will **automatically connect** your phone over Wi-Fi and **launch the BCI GUI app** for you instantly!
2. **`Start_BCI_App.bat`**:
   * Double-click this to launch the BCI GUI app directly (if your phone is already connected or if you are controlling the PC browser).

---

## 📱 How to Connect Your Android Phone (Manual Terminal Method)

If you prefer using the command prompt/terminal:

### Step 1: One-Time Pairing (Already Completed!)
Your phone and PC are already successfully paired. You do not need to do this step again unless you reset your phone's Developer Options.
* *For reference, the pairing command was:*
  `python scratch/pair_helper.py <IP>:<Pairing_Port> <Pairing_Code>`

### Step 2: Connect Your Phone (Do this each time you start)
Every time your phone locks, restarts, or reconnects to Wi-Fi, Android changes the wireless port for security. To connect:
1. Make sure your phone and PC are on the same Wi-Fi network.
2. On your phone, go to **Settings > Developer Options > Wireless debugging** (tap the text).
3. Look at the numbers shown under **IP address and port** (e.g. `192.168.185.138:42185`).
4. Open a Command Prompt or PowerShell on your PC, type this command, and press **Enter**:
   ```powershell
   python scratch/connect_wireless.py 192.168.185.138:<PORT>
   ```
   *(Replace `<PORT>` with the actual 5-digit number shown on your phone!)*

### Step 3: Run the BCI Application
Once the phone is connected, start the application:
```powershell
python bci_app.py
```

---

## 🎮 How to Control JioSaavn

1. In the BCI App GUI sidebar, set the **Control Target** to **Mobile** (for your phone) or **PC** (for your PC browser).
2. Toggle **Simulation Mode** to **ON** to start streaming simulated brain commands, or click **Connect Headset** to use your real Emotiv headset.
3. Watch the commands control playback in real-time!

### BCI Mind Command Mapping
| Mind Command | Simulated Action | What it triggers on JioSaavn |
| :--- | :--- | :--- |
| **Push** | Play / Pause | Plays or pauses the music |
| **Left** | Previous Track | Plays the previous song |
| **Right** | Next Track | Plays the next song |
| **Pull** | Volume Up | Increases the volume |
| **Lift** | Volume Down | Decreases the volume |
| **Pop** | Home | Launches / opens the JioSaavn app |
| **Think** | Search | Performs a randomized search in the app |

---

## ⚡ Useful Reconnection Cheat Sheet

| Task | Command to run | When to use |
| :--- | :--- | :--- |
| **Connect Phone** | `python scratch/connect_wireless.py 192.168.185.138:<PORT>` | Run this first every time you want to play music |
| **Check Connection** | `bin\adb\adb.exe devices` | To verify if your phone is still connected successfully |
| **Start BCI App** | `python bci_app.py` | To start the graphic control interface |

---

## 🔬 How it Works: From Brain Microvolts to JioSaavn Commands

If you have ever wondered how this project turns faint electrical activity in your skull into concrete music commands, here is the scientific physical-to-digital pipeline under the hood:

### 1. The Source: Electrical Brain Activity ($\mu\text{V}$)
Your brain contains billions of active neurons. When thousands of these neurons fire in synchronization in response to your thoughts or intentions, they generate tiny electrical potential fields. 
* These fields travel through the brain tissue, skull, and scalp.
* On the scalp, their amplitude is incredibly faint—typically between **$10$ to $100\text{ microvolts }(\mu\text{V})$** (a standard AA battery is $1.5\text{V}$, which is up to $150,000$ times stronger!).
* The **Emotiv EPOC X headset** uses sensitive scalp electrodes to pick up these minute voltage oscillations relative to a reference electrode.

### 2. Preprocessing & Noise Filtering (DSP)
Before any machine learning takes place, the signal must be isolated from noise (such as eye blinks, muscle clenches, or $50/60\text{Hz}$ powerline hum).
* The script applies a **4th-order Butterworth Bandpass Filter ($1.0 - 45.0\text{ Hz}$)**.
* This filters out slow skin-sweat drifts and fast device noise, preserving the core electroencephalogram (EEG) bands: **Delta** ($1-4\text{Hz}$), **Theta** ($4-8\text{Hz}$), **Alpha** ($8-12\text{Hz}$), **Beta** ($12-30\text{Hz}$), and **Gamma** ($30-45\text{Hz}$).

### 3. Feature Extraction
To help the classifier make decisions, the raw filtered microvolt time-series data is split into rolling 16-sample windows, and three key mathematical characteristics are calculated:
* **RMS (Root Mean Square) Energy:** Measures the physical amplitude power across all 32 channels.
* **Hemispheric Asymmetry:** Calculates `Left_Energy - Right_Energy`. When you focus on specific motor imagery actions (like imagining moving or pushing), one half of the motor cortex exhibits changes in activation compared to the other.
* **Zero Crossing Rate (ZCR):** Counts how often the signal crosses the zero baseline, representing its frequency signature.

### 4. StandardScaler Normalization
Due to hair thickness or sensor positioning, signal amplitudes can vary across sessions. A `StandardScaler` standardizes the extracted features (shifting mean to `0` and scaling variance to `1`) to keep inferences robust.

### 5. Neural Network Classification
Finally, the normalized features are passed to a trained **MLP (Multi-Layer Perceptron) Neural Network**.
* The network is trained to classify the current window into 1 of 8 states (`neutral` + 7 active commands).
* In real-time, it outputs a confidence probability (e.g. `87% pop push`). If this confidence exceeds the threshold (configured at $50\%$), the app routes the corresponding play/pause or track skipping action to the browser or Android device!
