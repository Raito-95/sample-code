import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import datetime
import time
from collections import deque

# Initial data recording time and time threshold
first_data_time = datetime.datetime.now()
time_threshold = datetime.timedelta(seconds=300)

# Initial filename
filename = f"data_{first_data_time.strftime('%Y%m%d%H%M%S')}.txt"

# Define an exponential smoothing function
def exponential_smoothing(data, alpha=0.2):
    smoothed_data = [data[0]]
    for i in range(1, len(data)):
        smoothed_value = alpha * data[i] + (1 - alpha) * smoothed_data[i-1]
        smoothed_data.append(smoothed_value)
    return smoothed_data

# Save data to a text file
def save_data_to_txt(data):
    global filename  # Make filename a global variable
    with open(filename, 'a') as file:
        file.write(data + '\n')

# Serial settings class
class SerialSettings:
    def __init__(self, master):
        # Create the main window
        self.master = master
        self.master.title('GUI')
        self.master.resizable(False, False)
        self.is_running = False

        # Create the serial port selection label and dropdown
        tk.Label(self.master, text="Port:").grid(row=0, column=0, sticky="E", pady=(10, 0))
        self.port_var = tk.StringVar()
        self.port_dropdown = tk.OptionMenu(self.master, self.port_var, *self.get_available_ports())
        self.port_dropdown.grid(row=0, column=1, sticky="N", pady=(10, 0))

        # Create the baud rate label and dropdown
        tk.Label(self.master, text="Baud Rate:").grid(row=1, column=0, sticky="E", pady=(10, 0))
        self.baud_var = tk.StringVar()
        self.baud_dropdown = tk.OptionMenu(self.master, self.baud_var, "115200")
        self.baud_dropdown.grid(row=1, column=1, sticky="N", pady=(10, 0))

        # Create the "Start" button
        self.start_button = tk.Button(self.master, text="Start", command=self.ok_clicked)
        self.start_button.grid(row=0, column=2, sticky="N", pady=(10, 0))

        # Create the "Stop" button
        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop_clicked)
        self.stop_button.grid(row=1, column=2, sticky="N", pady=(10, 0))

        # Create the status label
        self.status_label = tk.Label(self.master, text="Status: Not connected.")
        self.status_label.grid(row=2, column=0, columnspan=3, sticky="N", pady=(10, 0))

        self.frame_count = 0

    # Get all available serial ports
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = []

        for port, desc, hwid in sorted(ports):
            if "USB" in desc or "COM" in desc:
                port_list.append(port)

        return port_list

    # "Start" button click event
    def ok_clicked(self):
        # Get the selected serial port and baud rate
        selected_port = self.port_var.get()
        selected_baud = int(self.baud_var.get())

        # Handle the selected serial port and baud rate
        print(f"Selected port: {selected_port}, baud rate: {selected_baud}")

        COM_PORT = str(selected_port)
        BAUD_RATES = str(selected_baud)
        ser = serial.Serial(COM_PORT, BAUD_RATES)

        buff = [deque([], maxlen=max_length) for _ in range(3)]

        self.is_running = True

        # Update the status label to connected
        self.status_label["text"] = f"Status: Connected to {selected_port}"

        try:
            plt.ion()
            while self.is_running:
                current_time = datetime.datetime.now()
                time_difference = current_time - first_data_time
                print(f'time: {time_threshold - time_difference}')
                if time_difference > time_threshold:
                    self.is_running = False
                    print('Finish')
                self.process_data(ser, buff)
                self.draw_plots(buff)

        except Exception as e:
            print(f"An error occurred: {e}")
            plt.ioff()

        # Close the plot window
        plt.close()

        # Close the serial port
        ser.close()

        # Update the status label
        self.status_label["text"] = f"Status: Disconnected {selected_port}"

        # Close the window
        self.master.destroy()

    # "Stop" button click event
    def stop_clicked(self):
        # Clear the running flag
        self.is_running = False

    # Process serial data
    def process_data(self, ser, buff):
        try:
            data_raw = ser.readline()
            data = data_raw.decode()
            values = data.split("\n")
            for value in values:
                if value.startswith("rightOrigVolt1"):
                    rightOrigVolt1 = float(value.split(":")[1].strip())
                    buff[0].append(rightOrigVolt1)
                elif value.startswith("rightOrigVolt2"):
                    rightOrigVolt2 = float(value.split(":")[1].strip())
                    buff[1].append(rightOrigVolt2)
                elif value.startswith("Panel temperature"):
                    panelTemperature = float(value.split(":")[1].strip())
                    buff[2].append(panelTemperature)
        except serial.SerialException:
            print("Serial port reading failed, attempting to reconnect.")
            time.sleep(1)
        except ValueError:
            print("Data format error, will try to correct it.")

    # Draw data plots
    def draw_plots(self, buff):
        plt.clf()

        # Draw plots for rightOrigVolt1 and rightOrigVolt2
        plt.subplot(2, 1, 1)
        buff_arr1 = np.array(list(buff[0]))
        buff_arr2 = np.array(list(buff[1]))
        plt.plot(buff_arr1, color='y', label='Volt1')
        plt.plot(buff_arr2, color='m', label='Volt2')
        plt.title('Voltage')
        plt.xlabel('Signal')
        plt.ylabel('Voltage')
        plt.grid(True)
        plt.ylim(0.9, 2.2)
        plt.legend(loc='upper left')

        # Annotate the latest values for Volt1 and Volt2
        if len(buff[0]) > 1 and len(buff[1]) > 1:
            latest_value0 = buff_arr1[-1]
            latest_value1 = buff_arr2[-1]
            plt.annotate(f'{latest_value0:.3f}', (len(buff_arr1)-1, latest_value0),
                        xytext=(-10, 10), textcoords='offset points', color='y')
            plt.annotate(f'{latest_value1:.3f}', (len(buff_arr2)-1, latest_value1),
                        xytext=(-10, 10), textcoords='offset points', color='m')

        # Smooth the data in buff[2]
        if len(buff[2]) > 0:
            smoothed_buff = exponential_smoothing(buff[2])
        else:
            smoothed_buff = buff[2]

        # Draw original and smoothed data
        plt.subplot(2, 1, 2)
        buff_arr3 = np.array(buff[2])
        smoothed_buff_arr = np.array(smoothed_buff)
        plt.plot(smoothed_buff_arr, color='c', label='Smoothed')
        plt.plot(buff_arr3, color='lightgray', linestyle='--', label='Original')
        plt.title('Temperature')
        plt.xlabel('Signal')
        plt.ylabel('Temperature')
        plt.grid(True)
        plt.ylim(30, 110)
        plt.legend(loc='upper left')

        # Annotate the latest temperature value
        if len(smoothed_buff) > 1:
            latest_value2 = smoothed_buff_arr[-1]
            plt.annotate(f'{latest_value2:.2f}', (len(smoothed_buff_arr)-1, latest_value2),
                        xytext=(-10, 10), textcoords='offset points', color='c')
            self.frame_count += 1
            if self.frame_count % 5 == 0:
                save_date = f'{latest_value2:.2f}'
                save_data_to_txt(save_date)
                self.frame_count = 0

        plt.subplots_adjust(hspace=0.5)
        plt.draw()
        plt.pause(0.1)

# Maximum data length
max_length = 100

# Create the main window
root = tk.Tk()

# Create a SerialSettings object
serial_settings = SerialSettings(root)

# Start the main event loop
root.mainloop()
