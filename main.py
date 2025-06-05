import sys
import csv
import time
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGridLayout, QComboBox, QMessageBox, QFileDialog, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import serial
import serial.tools.list_ports

def find_arduino_ports():
    ports = serial.tools.list_ports.comports()
    common_descriptors = ["COM", "/dev/cu.usbmodem", "/dev/cu.usbserial", "/dev/ttyUSB", "/dev/ttyACM"]
    return [port for port in ports if any(desc in port.device for desc in common_descriptors)]

BAUD_RATE = 9600
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILE_NAME = f'log_files/voltage_log_real_time_{current_time}.csv'

with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time'] + [f'Channel{i+1}' for i in range(8)] + ['Threshold', 'Status', 'Label'])

class DAQWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arduino 8-Channel DAQ Logger")
        self.resize(800, 400)
        self.ser = None
        self.save_file_path = None
        self.acquisition_started = False

        self.port_selector = QComboBox()
        self.refresh_ports()
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter label")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_acquisition)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_acquisition)

        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_data_to_file)

        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(0, 1000)
        self.threshold_input.setValue(100)
        self.threshold_input.setSuffix(" mV")

        self.led_label = QLabel("●")
        self.led_label.setStyleSheet("color: gray; font-size: 18px")

        self.voltage_boxes = [QLineEdit() for _ in range(8)]
        for box in self.voltage_boxes:
            box.setReadOnly(True)
            box.setFixedWidth(80)

        self.delta_labels = [QLabel() for _ in range(8)]
        for label in self.delta_labels:
            label.setStyleSheet("font-size: 9pt")

        voltage_display = QGridLayout()
        for i in range(4):
            voltage_display.addWidget(QLabel(f"Ch {i+1} (mV):"), i, 0)
            voltage_display.addWidget(self.voltage_boxes[i], i, 1)
            voltage_display.addWidget(self.delta_labels[i], i, 2)
        for i in range(4, 8):
            voltage_display.addWidget(QLabel(f"Ch {i+1} (mV):"), i - 4, 3)
            voltage_display.addWidget(self.voltage_boxes[i], i - 4, 4)
            voltage_display.addWidget(self.delta_labels[i], i - 4, 5)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMinimumHeight(200)
        self.plot_widget.setLabel('left', 'Voltage (mV)', **{'font-size': '9pt'})
        self.plot_widget.setLabel('bottom', 'Time (s)', **{'font-size': '9pt'})
        self.plot_widget.getPlotItem().getAxis('left').setStyle(tickFont=QFont('Arial', 8))
        self.plot_widget.getPlotItem().getAxis('bottom').setStyle(tickFont=QFont('Arial', 8))
        self.plot_widget.getPlotItem().getViewBox().setMouseEnabled(x=False, y=False)
        self.plot_widget.getPlotItem().showGrid(x=True, y=True)
        self.plot_widget.addLegend()

        self.buffer_size = 1000
        self.channel_count = 8
        self.data_buffers = [np.zeros(self.buffer_size) for _ in range(self.channel_count)]
        self.time_buffer = np.zeros(self.buffer_size)

        colors = ['r', 'g', 'b', 'm']
        line_styles = [Qt.SolidLine]*4 + [Qt.DashLine]*4
        self.curves = []
        for i in range(self.channel_count):
            pen = pg.mkPen(color=colors[i % 4], width=2, style=line_styles[i])
            curve = self.plot_widget.plot(pen=pen, name=f"Channel {i+1}")
            self.curves.append(curve)

        self.reset_button = QPushButton("Reset Zoom")
        self.reset_button.clicked.connect(self.reset_zoom)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Serial Port:"))
        port_layout.addWidget(self.port_selector)
        port_layout.addWidget(self.refresh_button)
        port_layout.addWidget(self.connect_button)
        port_layout.setSpacing(5)

        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Label:"))
        config_layout.addWidget(self.label_input)
        config_layout.addWidget(QLabel("Threshold:"))
        config_layout.addWidget(self.threshold_input)
        config_layout.addWidget(QLabel("Status:"))
        config_layout.addWidget(self.led_label)
        config_layout.setSpacing(5)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)
        button_layout.setSpacing(5)

        left_layout = QVBoxLayout()
        left_layout.addLayout(port_layout)
        left_layout.addLayout(config_layout)
        left_layout.addLayout(button_layout)
        left_layout.addLayout(voltage_display)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.plot_widget)
        right_layout.addWidget(self.reset_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=5)

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
            self.led_label.setStyleSheet("color: green; font-size: 18px")
            with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        else:
            QMessageBox.warning(self, "Start Error", "Serial port not connected.")

    def stop_acquisition(self):
        self.timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.write(b'X')
        self.acquisition_started = False
        self.led_label.setStyleSheet("color: gray; font-size: 18px")
        with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])

    def update_plot(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            parts = line.split(', ')
            if len(parts) != 9:
                print(f"Unexpected data format: {line}")
                return
            time_value = float(parts[0])
            voltages = [float(v) for v in parts[1:]]
            self.time_buffer = np.roll(self.time_buffer, -1)
            self.time_buffer[-1] = time_value

            for i in range(self.channel_count):
                self.voltage_boxes[i].setText(f"{voltages[i]:.1f}")
                self.data_buffers[i] = np.roll(self.data_buffers[i], -1)
                self.data_buffers[i][-1] = voltages[i]
                self.curves[i].setData(self.time_buffer, self.data_buffers[i])

            rebar_ref = min(-voltages[0], -voltages[1], -voltages[2], -voltages[3])
            threshold = self.threshold_input.value()
            label = self.label_input.text()
            warning_flag = False
            for i in range(4, 8):
                delta = -voltages[i] - rebar_ref
                text = f"Δϕ = {delta:.1f} mV"
                if delta > threshold:
                    self.delta_labels[i].setText(f"<b><font color='red'>{text}</font></b>")
                    warning_flag = True
                else:
                    self.delta_labels[i].setText(text)

            if warning_flag:
                self.led_label.setStyleSheet("color: red; font-size: 18px")
            elif self.acquisition_started:
                self.led_label.setStyleSheet("color: green; font-size: 18px")

            if self.time_buffer[-1] - self.time_buffer[0] > 0:
                self.plot_widget.setXRange(self.time_buffer[-1] - 10, self.time_buffer[-1])

            with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                status = "P" if warning_flag else "N"
                writer.writerow([time_value] + voltages + [threshold, status, label])
        except Exception as e:
            print(f"Error reading serial data: {e}")

    def save_data_to_file(self):
        if self.save_file_path is None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)")
            if file_path:
                self.save_file_path = file_path
                with open(self.save_file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Time'] + [f'Channel{i+1}' for i in range(8)] + ['Threshold', 'Status', 'Label'])
            else:
                return
        try:
            latest_time = self.time_buffer[-1]
            latest_values = [buffer[-1] for buffer in self.data_buffers]
            threshold = self.threshold_input.value()
            status = self.led_label.styleSheet().find("red") != -1
            label = self.label_input.text()
            with open(self.save_file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([latest_time] + latest_values + [threshold, "P" if status else "N", label])
            QMessageBox.information(self, "Save Successful", f"Latest data saved to {self.save_file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Error: {e}")

    def reset_zoom(self):
        if self.time_buffer[-1] - self.time_buffer[0] > 0:
            self.plot_widget.setXRange(self.time_buffer[-1] - 10, self.time_buffer[-1])
            min_v = min([min(buf[-100:]) for buf in self.data_buffers])
            max_v = max([max(buf[-100:]) for buf in self.data_buffers])
            margin = (max_v - min_v) * 0.1 if max_v != min_v else 0.1
            self.plot_widget.setYRange(min_v - margin, max_v + margin)

    def closeEvent(self, event):
        self.stop_acquisition()
        if self.ser:
            try:
                self.ser.close()
            except Exception as e:
                print(f"Error closing serial port: {e}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAQWidget()
    window.show()
    sys.exit(app.exec_())
