import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plot
import tkinter as tk
from tkinter import ttk
import threading
import datetime
import time
from collections import deque
import logging
import queue
# Set up logging
logging.basicConfig(filename='serial_gui.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
first_data_time = datetime.datetime.now()
filename = f"data_{first_data_time.strftime('%Y%m%d%H%M%S')}.txt"
def save_data_to_txt(data):
    global filename
    with open(filename, 'a') as file:
        file.write(data + '\n')
class SerialSettings:
    def __init__(self, master):
        self.data_queue = queue.Queue()
        self.master = master
        self.master.title('Serial Data GUI')
        self.master.resizable(False, False)
        self.is_running = False
        self.serial_connection = None
        # Configuration for data identifiers
        self.data_identifiers = {
            'RightTemperature': 0,
            'LeftTemperature': 1
        }
        style = ttk.Style()
        style.theme_use('default')  # You could also use 'clam' or 'alt'
        style.configure('TButton', background='#E1E1E1', foreground='black')
        style.configure('TLabel', background='#E1E1E1', foreground='black')
        style.configure('TFrame', background='#E1E1E1')
        style.configure('TEntry', background='white', foreground='black')
        tk.Label(self.master, text="Port:").grid(row=0, column=0, sticky="E", pady=(10, 0))
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.OptionMenu(self.master, self.port_var, *self.get_available_ports())
        self.port_dropdown.grid(row=0, column=1, sticky="N", pady=(10, 0))
        tk.Label(self.master, text="Baud Rate:").grid(row=1, column=0, sticky="E", pady=(10, 0))
        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.OptionMenu(self.master, self.baud_var, "9600", "19200", "38400", "57600", "115200")
        self.baud_dropdown.grid(row=1, column=1, sticky="N", pady=(10, 0))
        self.start_button = ttk.Button(self.master, text="Start", command=self.start_clicked)
        self.start_button.grid(row=0, column=2, sticky="N", pady=(10, 0))
        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_clicked, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=2, sticky="N", pady=(10, 0))
        self.exit_button = ttk.Button(self.master, text="Exit", command=self.exit_clicked)
        self.exit_button.grid(row=2, column=2, sticky="N", pady=(10, 0))
        self.status_label = tk.Label(self.master, text="Status: Not connected.")
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="N", pady=(10, 0))
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    def start_clicked(self):
        selected_port = self.port_var.get()
        selected_baud = self.baud_var.get()
        self.connect_serial(selected_port, selected_baud)
        if self.serial_connection and self.serial_connection.is_open:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.read_data_continuously()
    def stop_clicked(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.serial_connection:
            self.serial_connection.close()
            self.status_label["text"] = "Status: Disconnected"
    def exit_clicked(self):
        # Signal the thread to stop
        self.is_running = False
        time.sleep(0.1)  # Give a little time for the thread to respond to the stop signal
        # Close the serial connection if it's open
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        # Turn off the interactive mode of matplotlib
        plot.ioff()
        # Destroy the tkinter window to close the application
        self.master.destroy()
    def connect_serial(self, port, baud_rate):
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            self.status_label["text"] = f"Status: Connected to {port}"
            logging.info(f"Connected to {port} with baud rate {baud_rate}")
        except serial.SerialException as e:
            self.status_label["text"] = f"Connection failed: {e}"
            logging.error(f"Connection failed: {e}")
    def process_data(self, data_raw):
        try:
            # Decode the raw data received from the serial port
            data = data_raw.decode()
            # Split the data by line breaks and process each value
            values = data.split("\n")
            for value in values:
                for identifier, index in self.data_identifiers.items():
                    if value.startswith(identifier):
                        temperature = float(value.split(":")[1].strip())
                        self.buff[index].append(temperature)
                        # Save data to file or other processing
                        save_data_to_txt(value)
        except ValueError as e:
            print("Data format error, will try to correct it.", e)
    def draw_plots(self):
        plot.clf()
        buff_arr1 = np.array(list(self.buff[0]))
        buff_arr2 = np.array(list(self.buff[1]))
        plot.plot(buff_arr1, color='red', label='Right')
        plot.plot(buff_arr2, color='blue', label='Left')
        plot.title('Temperature Data')
        plot.xlabel('Time')
        plot.ylabel('Temperature (°C)')
        plot.legend(loc='upper left')
        plot.grid(True)
        plot.pause(0.1)
    def read_data_continuously(self):
        threading.Thread(target=self._read_data_thread, daemon=True).start()
    def _read_data_thread(self):
        self.buff = [deque(maxlen=100) for _ in range(len(self.data_identifiers))]
        plot.ion()
        while self.is_running:
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    data_raw = self.serial_connection.readline()
                    if data_raw:
                        self.process_data(data_raw)
                        # Instead of drawing the plot here, put the data in a queue
                        self.data_queue.put(self.buff)
                except serial.SerialException as e:
                    self.status_label["text"] = f"Lost connection: {e}. Attempting to reconnect..."
                    logging.warning(f"Lost connection: {e}. Attempting to reconnect...")
                    time.sleep(5)
                    self.connect_serial(self.port_var.get(), self.baud_var.get())
            else:
                self.status_label["text"] = "Connection closed. Attempting to reconnect..."
                logging.warning("Connection closed. Attempting to reconnect...")
                time.sleep(5)
                self.connect_serial(self.port_var.get(), self.baud_var.get())
        plot.ioff()
    def update_plot(self):
        try:
            # Get the latest data from the queue
            data = self.data_queue.get_nowait()
            plot.clf()
            colors = ['red', 'blue']  # List of colors for the plots
            for index, buff in enumerate(data):
                buff_array = np.array(list(buff))
                # Plot with the specified color and label
                plot.plot(buff_array, color=colors[index], label=f'Data {index}')
                # Annotate the latest data point
                if len(buff_array) > 0:
                    plot.annotate(f'{buff_array[-1]:.2f}',
                                xy=(len(buff_array)-1, buff_array[-1]),
                                textcoords="offset points",
                                xytext=(0,10),
                                ha='center', color=colors[index])
            plot.title('Temperature Data')
            plot.xlabel('Time')
            plot.ylabel('Temperature (°C)')
            plot.legend(loc='upper left')
            plot.grid(True)
            plot.draw()
        except queue.Empty:
            pass
        # Schedule the next plot update
        self.master.after(100, self.update_plot)
def main():
    root = tk.Tk()
    app = SerialSettings(root)
    # Start the periodic plot update
    app.update_plot()
    root.mainloop()
if __name__ == "__main__":
    main()