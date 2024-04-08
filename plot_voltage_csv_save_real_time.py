import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# Speed and Efficiency: Lower. Data is written to disk in real-time, resulting in frequent disk I/O operations. This can slow down the program, especially with high-frequency data, due to the overhead associated with each write operation.
# Robustness: High. Continuously saving data as it arrives minimizes the risk of data loss due to crashes or power outages. Most data is preserved, making this method more reliable for critical data logging.

# Constants
SERIAL_PORT = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600
CSV_FILE_NAME = 'voltage_log_real_time.csv'

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Initialize empty lists to store data
x_vals = []
voltage_1 = []

# Open the CSV file in append mode and write the header if the file is empty
with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Move the file pointer (cursor) to the end of the file.
    csvfile.seek(0, 2)
    # If we are at the start of the file, write the header
    if csvfile.tell() == 0:
        writer.writerow(['Time', 'Voltage1'])

# Create a function to read and process data from Arduino and append to CSV
def read_and_process_data():
    line = ser.readline().decode('utf-8').strip()
    line = line.split(', ')

    # Parse values
    time_value = float(line[0])
    voltage_value = float(line[1])

    # Append to the lists
    x_vals.append(time_value)
    voltage_1.append(voltage_value)

    # Append to CSV file
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([time_value, voltage_value])

    # Print the received values
    print(f'Time: {time_value}, Voltage 1: {voltage_value}', flush=True)

# Create a function to update the plot
def update_plot(frame):
    read_and_process_data()
    plt.cla()
    plt.plot(x_vals, voltage_1, label='Voltage 1')
    plt.xlabel('Time')
    plt.ylabel('Voltage (mV)')
    plt.legend()

# Create the plot
fig, ax = plt.subplots()

ani = FuncAnimation(fig, update_plot, interval=10, cache_frame_data=False)
plt.show()
