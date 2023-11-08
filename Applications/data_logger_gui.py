import logging
import queue
import re
import serial
import threading
from collections import deque
from tkinter import ttk
import tkinter as tk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial.tools.list_ports

matplotlib.use('TkAgg')

logging.basicConfig(filename='serial_gui.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

dict = {'RightTemperature': 0,
        'LeftTemperature': 1}

class DataProcessor:
    def __init__(self, identifiers, save_filename):
        self.data_identifiers = {re.compile(f'^{id}'): idx for id, idx in identifiers.items()}
        self.buff = [deque(maxlen=100) for _ in identifiers.values()]
        self.filename = save_filename

    def process_data(self, data_raw):
        try:
            data = data_raw.decode()
            values = data.split("\n")
            for value in values:
                for pattern, index in self.data_identifiers.items():
                    match = pattern.match(value)
                    if match:
                        temperature = float(value.split(":")[1].strip())
                        self.buff[index].append(temperature)
                        self.save_data_to_txt(value)
        except ValueError as e:
            logging.error("Data format error: %s", e)

    def save_data_to_txt(self, data):
        with open(self.filename, 'a') as file:
            file.write(data + '\n')

class SerialConnection:
    def __init__(self):
        self.serial_connection = None

    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port, baud_rate):
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            logging.info("Connected to %s with baud rate %s", port, baud_rate)
            return True
        except serial.SerialException as e:
            logging.error("Connection failed: %s", e)
            return False

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logging.info("Disconnected from the serial port")

    def read_data(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                return self.serial_connection.readline()
            except serial.SerialException as e:
                logging.warning("Read data failed: %s", e)
                self.disconnect()
                return None

class SerialGUI:
    def __init__(self, root, processor, connection):
        self.master = root
        self.data_processor = processor
        self.serial_connection = connection
        self.is_running = False
        self.data_thread = None
        self.data_queue = queue.Queue()
        self.after_id = None
        self.setup_gui()

    def setup_gui(self):
        self.master.title('Serial Data GUI')
        self.master.resizable(False, False)

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        port_label = ttk.Label(connection_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(connection_frame, textvariable=self.port_var, state="readonly")
        self.port_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        baud_label = ttk.Label(connection_frame, text="Baud Rate:")
        baud_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.Combobox(connection_frame, textvariable=self.baud_var, state="readonly")
        self.baud_dropdown['values'] = ("9600", "19200", "38400", "57600", "115200")
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicked)
        self.start_button.pack(side=tk.LEFT, padx=(10, 5), pady=5, fill=tk.BOTH, expand=True)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicked, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_clicked)
        self.exit_button.pack(side=tk.LEFT, padx=(5, 10), pady=5, fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar()
        self.status_var.set("Status: Not connected")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.update_ports_periodically()
        self.update_ports()
        self.update_plot()

    def update_ports_periodically(self):
        available_ports = self.serial_connection.get_available_ports()
        self.port_dropdown['values'] = available_ports
        if available_ports:
            self.port_dropdown.set(available_ports[0])
        self.after_id = self.master.after(5000, self.update_ports_periodically)

    def update_ports(self):
        available_ports = self.serial_connection.get_available_ports()
        self.port_dropdown['values'] = available_ports
        if available_ports:
            self.port_dropdown.set(available_ports[0])
            
    def start_clicked(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.serial_connection.connect(self.port_var.get(), self.baud_var.get())
        self.data_thread = threading.Thread(target=self.read_data_thread, daemon=True)
        self.data_thread.start()
        self.update_plot()
        self.status_var.set("Status: Connected to Serial Port")

    def stop_clicked(self):
        self.is_running = False
        self.serial_connection.disconnect()
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.status_var.set("Status: Not connected")

    def exit_clicked(self):
        self.stop_clicked()
        if self.after_id:
            self.master.after_cancel(self.after_id)
        self.master.quit()

    def read_data_thread(self):
        while self.is_running:
            data_raw = self.serial_connection.read_data()
            if data_raw:
                self.data_processor.process_data(data_raw)
                self.data_queue.put((self.data_processor.buff[0].copy(), self.data_processor.buff[1].copy()))
        self.cleanup_thread()

    def cleanup_thread(self):
        if self.data_thread is not None:
            self.data_thread = None

    def update_plot(self):
        if not self.data_queue.empty():
            right_temperature, left_temperature = self.data_queue.get_nowait()
            self.plot.clear()
            
            self.plot.plot(right_temperature, label='Right Temperature', color='red')
            
            self.plot.plot(left_temperature, label='Left Temperature', color='blue')

            self.plot.set_xlabel('Time')
            self.plot.set_ylabel('Temperature (°C)')

            if right_temperature and left_temperature:
                last_right_temp = right_temperature[-1]
                last_left_temp = left_temperature[-1]
                self.plot.annotate(f'{last_right_temp:.2f}', (len(right_temperature) - 1, last_right_temp), textcoords="offset points", xytext=(0,10), ha='center', color='red')
                self.plot.annotate(f'{last_left_temp:.2f}', (len(left_temperature) - 1, last_left_temp), textcoords="offset points", xytext=(0,10), ha='center', color='blue')
            
            self.plot.legend(loc='upper left')
            self.canvas.draw_idle()
        self.after_id = self.master.after(1000, self.update_plot)

def main():
    root = tk.Tk()
    processor = DataProcessor(dict,
                              "data.txt")
    connection = SerialConnection()
    SerialGUI(root, processor, connection)
    root.mainloop()

if __name__ == "__main__":
    main()
