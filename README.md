# 8-Channel Voltage Logger using ADS1115 and PyQt5

This project is a simple data acquisition system that uses two **ADS1115** ADC modules connected to an **Arduino Nano**, logging 8 analog voltage channels and plotting them in real-time using a **Python PyQt5 GUI**.

## Features

- Reads 8 analog voltages via two ADS1115s over I²C
- Real-time voltage plotting with PyQtGraph
- Save data to CSV file with timestamp
- Start/stop acquisition from GUI
- Reset zoom functionality on plot

## Hardware Setup

- **Microcontroller:** Arduino Nano (ATmega328P)
- **ADC Modules:** 2x Adafruit ADS1115
  - One with ADDR connected to **GND** (I²C address 0x48)
  - One with ADDR connected to **VDD** (I²C address 0x49)
- I²C Bus: Connect both ADS1115 modules to the same I²C lines (A4 for SDA, A5 for SCL on Nano)
- Connect analog signal sources to AIN0–AIN3 on both ADS1115s

## File Structure

```
.
├── main.py               # PyQt5 GUI application
├── voltmeter_8ch.ino         # Arduino sketch for reading ADS1115
├── log_files/            # Directory to store CSV log files
└── README.md             # Project documentation
```

## Getting Started

### 1. Upload Arduino Sketch

- Open `voltmeter_8ch.ino` in the Arduino IDE.
- Select board type **"Arduino Nano"** and processor **"ATmega328P"**.
- Upload the sketch.

### 2. Install Python Dependencies

Make sure Python 3 is installed. Then install required libraries:

```bash
pip install pyqt5 pyqtgraph pyserial numpy
```

### 3. Run the GUI

```bash
python main.py
```

## GUI Overview

- **Port Selection:** Choose the correct serial port for the Arduino Nano.
- **Start Acquisition:** Starts reading and logging voltages from all 8 channels.
- **Stop Acquisition:** Stops data logging and plot updates.
- **Save Data to CSV:** Manually save the latest data snapshot.
- **Reset Zoom:** Re-focuses plot on the current 10-second window.

## Notes

- Data is logged automatically every second.
- CSV files are saved to `log_files/voltage_log_real_time_*.csv`.
- By default, 4 solid lines represent channels 1–4, and 4 dashed lines represent channels 5–8.

## License

This project is provided under the MIT License. See `LICENSE` file for details.
