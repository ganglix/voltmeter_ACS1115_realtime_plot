import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime

# Constants
SERIAL_PORT = '/dev/cu.usbmodem143101'
BAUD_RATE = 9600

# Generate a unique file name using the current date and time
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILE_NAME = f'voltage_log_real_time_{current_time}.csv'

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Initialize empty lists to store data
x_vals = []
voltage_1 = []
voltage_2 = []
voltage_3 = []
voltage_4 = []

# Open the CSV file in append mode and write the header if the file is empty
with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Check if the file is empty to write the header
    if csvfile.tell() == 0:
        writer.writerow(['Time', 'Voltage1', 'Voltage2', 'Voltage3', 'Voltage4'])

# Function to read and process data from Arduino and append to CSV
def read_and_process_data():
    line = ser.readline().decode('utf-8').strip()
    line = line.split(', ')

    # Parse values
    time_value = float(line[0])
    voltage_values = [float(v) for v in line[1:]]  # Assuming the rest are voltage values

    # Append to the lists
    x_vals.append(time_value)
    voltage_1.append(voltage_values[0])
    voltage_2.append(voltage_values[1])
    voltage_3.append(voltage_values[2])
    voltage_4.append(voltage_values[3])

    # Append to CSV file
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([time_value] + voltage_values)

    # Print the received values
    print(f'Time: {time_value}, Voltages: {voltage_values}', flush=True)

# Function to update the plot
def update_plot(frame):
    read_and_process_data()
    plt.cla()
    plt.plot(x_vals, voltage_1, label='Voltage 1')
    plt.plot(x_vals, voltage_2, label='Voltage 2')
    plt.plot(x_vals, voltage_3, label='Voltage 3')
    plt.plot(x_vals, voltage_4, label='Voltage 4')
    plt.xlabel('Time')
    plt.ylabel('Voltage (mV)')
    plt.legend()

# Create the plot
fig, ax = plt.subplots()

ani = FuncAnimation(fig, update_plot, interval=1000)  # Adjust interval as needed
plt.show()
