import serial 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# Speed and Efficiency: High. Data is stored in memory and written to disk in a single operation upon closing the plot. This minimizes disk I/O operations, making it faster and more efficient for large datasets.
# Robustness: Low. This method risks significant data loss in case of unexpected shutdowns or crashes, as all unsaved data in memory will be lost.

# Constants
SERIAL_PORT = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, 9600)  # Open serial port at 9600 baud rate

# Initialize empty lists to store data
x_vals = []
voltage_1 = []

# Create a function to read and process data from Arduino
def read_and_process_data():
    line = ser.readline().decode('utf-8').strip()
    line = line.split(', ')

    x_vals.append(float(line[0]))
    voltage_1.append(float(line[1]))

    # Print the received values
    print(f'Time: {line[0]}, Voltage 1: {line[1]}')

# Create a function to update the plot
def update_plot(frame):
    read_and_process_data()
    plt.cla()
    plt.plot(x_vals, voltage_1, label='voltage 1')
    plt.xlabel('Time')
    plt.ylabel('Voltage (mV)')
    plt.legend()

# Create a function to save data to a CSV file when the plot window is closed
def on_close(event):
    with open('voltage_log.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Voltage1'])
        for x, v1 in zip(x_vals, voltage_1):
            writer.writerow([x, v1])

# Register the callback function for when the plot window is closed
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)

ani = FuncAnimation(fig, update_plot, interval=10, cache_frame_data=False)
plt.show()
