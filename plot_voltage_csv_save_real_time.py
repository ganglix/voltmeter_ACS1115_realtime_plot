import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime
from serial.tools import list_ports  # Import the list_ports tool

def find_arduino_ports():
    """This function finds all ports that might be connected to an Arduino."""
    ports = serial.tools.list_ports.comports()
    common_descriptors = [
        "COM",  # Common descriptor on Windows
        "/dev/cu.usbmodem",  # Common on macOS
        "/dev/cu.usbserial",  # Also found on macOS
        "/dev/ttyUSB",  # Common on Linux
        "/dev/ttyACM"  # Also found on Linux
    ]
    
    matching_ports = [port.device for port in ports if any(descriptor in port.device for descriptor in common_descriptors)]
    
    if not matching_ports:
        print("Arduino not found. Please connect your Arduino device or")
        return input("Manually type in the PortName: ")
    elif len(matching_ports) == 1:
        print(f"Arduino found on port: {matching_ports[0]}")
        return matching_ports[0]
    else:
        print("Multiple Arduino devices found. Please choose one:")
        for index, port in enumerate(matching_ports):
            print(f"{index + 1}: {port}")
        choice = int(input("Enter the number of the Arduino you want to connect to: "))
        return matching_ports[choice - 1]

# Using the function
SERIAL_PORT = find_arduino_ports()

# Constants

BAUD_RATE = 9600

# Generate a unique file name using the current date and time
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILE_NAME = f'log_files/voltage_log_real_time_{current_time}.csv'

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
except serial.SerialException:
    print("Failed to connect to serial port.")
    exit(1)

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
    # voltage_2.append(voltage_values[1])
    # voltage_3.append(voltage_values[2])
    # voltage_4.append(voltage_values[3])

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
    # plt.plot(x_vals, voltage_2, label='Voltage 2')
    # plt.plot(x_vals, voltage_3, label='Voltage 3')
    # plt.plot(x_vals, voltage_4, label='Voltage 4')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (mV)')
    plt.legend()

# Create the plot
fig, ax = plt.subplots()

ani = FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False)  # Adjust interval as needed
plt.show()
