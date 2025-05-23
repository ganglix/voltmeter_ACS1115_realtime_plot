import sys
import csv
import time
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGridLayout, QComboBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
import serial
import serial.tools.list_ports

def find_arduino_ports():
    ports = serial.tools.list_ports.comports()
    common_descriptors = [
        "COM", "/dev/cu.usbmodem", "/dev/cu.usbserial", "/dev/ttyUSB", "/dev/ttyACM"
    ]
    matching_ports = [port for port in ports if any(desc in port.device for desc in common_descriptors)]
    return matching_ports

BAUD_RATE = 9600
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILE_NAME = f'log_files/voltage_log_real_time_{current_time}.csv'
with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time', 'Channel1', 'Channel2', 'Channel3', 'Channel4'])

class DAQWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arduino 4-Channel DAQ Logger")
        self.resize(1200, 500)
        self.ser = None
        self.save_file_path = None
        self.acquisition_started = False

        self.port_selector = QComboBox()
        self.refresh_ports()
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)

        self.start_button = QPushButton("Start Acquisition")
        self.start_button.clicked.connect(self.start_acquisition)

        self.stop_button = QPushButton("Stop Acquisition")
        self.stop_button.clicked.connect(self.stop_acquisition)

        self.save_button = QPushButton("Save Data to CSV")
        self.save_button.clicked.connect(self.save_data_to_file)

        self.voltage_boxes = [QLineEdit() for _ in range(4)]
        for box in self.voltage_boxes:
            box.setReadOnly(True)

        voltage_display = QGridLayout()
        for i, box in enumerate(self.voltage_boxes):
            voltage_display.addWidget(QLabel(f"Channel {i+1} (mV):"), i, 0)
            voltage_display.addWidget(box, i, 1)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Voltage (mV)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.addLegend()

        self.buffer_size = 1000
        self.channel_count = 4
        self.data_buffers = [np.zeros(self.buffer_size) for _ in range(self.channel_count)]
        self.time_buffer = np.zeros(self.buffer_size)

        colors = ['r', 'g', 'b', 'm']
        styles = [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine]
        self.curves = []
        for i in range(self.channel_count):
            pen = pg.mkPen(color=colors[i], width=2, style=styles[i])
            curve = self.plot_widget.plot(pen=pen, name=f"Channel {i+1}")
            self.curves.append(curve)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Serial Port:"))
        port_layout.addWidget(self.port_selector)
        port_layout.addWidget(self.refresh_button)
        port_layout.addWidget(self.connect_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)

        left_layout = QVBoxLayout()
        left_layout.addLayout(port_layout)
        left_layout.addLayout(button_layout)
        left_layout.addLayout(voltage_display)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addWidget(self.plot_widget, stretch=3)

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def refresh_ports(self):
        self.port_selector.clear()
        ports = find_arduino_ports()
        if not ports:
            self.port_selector.addItem("No devices found")
        for port in ports:
            self.port_selector.addItem(f"{port.device} - {port.description}", port.device)

    def connect_device(self):
        selected_index = self.port_selector.currentIndex()
        if selected_index == -1 or "No devices" in self.port_selector.currentText():
            QMessageBox.warning(self, "Connection Error", "No valid serial port selected.")
            return
        port_name = self.port_selector.currentData()
        try:
            self.ser = serial.Serial(port_name, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.ser.reset_input_buffer()
            QMessageBox.information(self, "Success", f"Connected to {port_name}")
        except Exception as e:
            QMessageBox.critical(self, "Serial Error", f"Failed to connect: {e}")

    def start_acquisition(self):
        if self.ser and self.ser.is_open:
            self.ser.write(b'S')
            self.timer.start(1000)
            self.acquisition_started = True
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([])
                    writer.writerow([f"Acquisition started at {start_time}"])
                    writer.writerow([])
            except Exception as e:
                print(f"Error logging start time: {e}")
            print("Started data acquisition.")
        else:
            QMessageBox.warning(self, "Start Error", "Serial port not connected.")

    def stop_acquisition(self):
        self.timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.write(b'X')
            print("Serial stop signal sent.")
        stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([])
                writer.writerow([f"Acquisition stopped at {stop_time}"])
                writer.writerow([])
        except Exception as e:
            print(f"Error logging stop time: {e}")
        self.acquisition_started = False
        print("Stopped data acquisition.")

    def update_plot(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            parts = line.split(', ')
            if len(parts) != 5:
                print(f"Unexpected data format: {line}")
                return
            time_value = float(parts[0])
            voltages = [float(v) for v in parts[1:]]
            self.time_buffer = np.roll(self.time_buffer, -1)
            self.time_buffer[-1] = time_value
            for i in range(4):
                self.voltage_boxes[i].setText(f"{voltages[i]:.2f}")
                self.data_buffers[i] = np.roll(self.data_buffers[i], -1)
                self.data_buffers[i][-1] = voltages[i]
                self.curves[i].setData(self.time_buffer, self.data_buffers[i])
            if self.time_buffer[-1] - self.time_buffer[0] > 0:
                self.plot_widget.setXRange(self.time_buffer[-1] - 10, self.time_buffer[-1])
            with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([time_value] + voltages)
        except Exception as e:
            print(f"Error reading serial data: {e}")

    def save_data_to_file(self):
        if self.save_file_path is None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                self.save_file_path = file_path
                with open(self.save_file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Time', 'Channel1', 'Channel2', 'Channel3', 'Channel4'])
            else:
                return
        try:
            latest_time = self.time_buffer[-1]
            latest_values = [buffer[-1] for buffer in self.data_buffers]
            with open(self.save_file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([latest_time] + latest_values)
            QMessageBox.information(self, "Save Successful", f"Latest data saved to {self.save_file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Error: {e}")

    def closeEvent(self, event):
        self.stop_acquisition()
        if self.ser:
            try:
                self.ser.close()
                print("Serial port closed.")
            except Exception as e:
                print(f"Error closing serial port: {e}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAQWidget()
    window.show()
    sys.exit(app.exec_())
