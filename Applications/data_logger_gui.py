import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re
import serial
from collections import deque

# Constants for the buffer size
BUFFER_SIZE = 100
# Constants for number of lines to read at once
NUM_LINES_TO_READ = 2

# Main application class
class SerialDataGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # master should be a Tk instance
        self.serial_port = None
        self.after_id = None
        # Initialize deques with a fixed size
        self.right_temperatures = deque(maxlen=BUFFER_SIZE)
        self.left_temperatures = deque(maxlen=BUFFER_SIZE)
        self.setup_gui()

    def setup_gui(self):
        self.master.title('Serial Data GUI')  # type: ignore
        self.master.resizable(False, False)   # type: ignore

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        port_label = ttk.Label(connection_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(connection_frame, textvariable=self.port_var, state="readonly")
        self.port_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Using a Unicode symbol to represent refresh
        refresh_text = "\u21BB"  # This is the Unicode character for a clockwise open circle arrow
        self.refresh_button = ttk.Button(connection_frame, text=refresh_text, command=self.update_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        baud_label = ttk.Label(connection_frame, text="Baud Rate:")
        baud_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_dropdown = ttk.Combobox(connection_frame, textvariable=self.baud_var, state="readonly")
        self.baud_dropdown['values'] = ("9600", "19200", "38400", "57600", "115200")
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicked)
        self.start_button.pack(side=tk.LEFT, padx=(10, 5), pady=5, fill=tk.BOTH, expand=True)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicked, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.clear_button  = ttk.Button(button_frame, text="Clear", command=self.clear_plot)
        self.clear_button .pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.master.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=(5, 10), pady=5, fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar()
        self.status_var.set("Status: Not connected")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_ports_periodically()
        self.update_ports()

    def update_ports(self):
        if self.start_button['state'] == 'disabled':  # System is started, don't update ports
            return
        current_port = self.port_var.get()
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        self.port_dropdown['values'] = ports
        if current_port in ports:
            self.port_var.set(current_port)  # Keep the current selection if available
        elif ports:
            self.port_var.set(ports[0])  # Default to the first port if available
        else:
            self.port_var.set('')  # No ports available

    def update_ports_periodically(self):
        self.update_ports()
        self.after(5000, self.update_ports_periodically)  # Update every 5 seconds

    def start_clicked(self):
        try:
            baud_rate = int(self.baud_var.get())
            self.serial_port = serial.Serial(self.port_var.get(), baud_rate, timeout=1)
            self.status_var.set(f"Connected to {self.port_var.get()} at {baud_rate} baud.")
            
            # Disable port and baud rate controls
            self.port_dropdown['state'] = 'disabled'
            self.baud_dropdown['state'] = 'disabled'
            self.refresh_button['state'] = 'disabled'
            
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'
            self.update_plot()
        except serial.SerialException as e:
            self.status_var.set(f"Error: {e}")
        except ValueError as e:
            self.status_var.set(f"Invalid baud rate: {self.baud_var.get()}")

    def stop_clicked(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        if self.after_id:
            self.master.after_cancel(self.after_id)
        
        # Re-enable port and baud rate controls
        self.port_dropdown['state'] = 'readonly'
        self.baud_dropdown['state'] = 'readonly'
        self.refresh_button['state'] = 'normal'
        
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'
        self.status_var.set("Stopped.")

    def read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            for _ in range(NUM_LINES_TO_READ):
                line = self.serial_port.readline().decode('utf-8').rstrip()
                right_match = re.search(r"RightTemperature:\s*(\d+\.?\d*)", line)
                left_match = re.search(r"LeftTemperature:\s*(\d+\.?\d*)", line)
                if right_match:
                    self.right_temperatures.append(float(right_match.group(1)))
                if left_match:
                    self.left_temperatures.append(float(left_match.group(1)))

    def clear_plot(self):
        # Clear the temperature data lists
        self.right_temperatures.clear()
        self.left_temperatures.clear()

        # Clear the plot
        self.plot.clear()
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Temperature (°C)')
        self.canvas.draw_idle()

    def update_plot(self):
        self.read_serial()
        self.plot.clear()

        # print(f"Right Temps: {self.right_temperatures}")  # Debugging print statement
        # print(f"Left Temps: {self.left_temperatures}")    # Debugging print statement

        # Plot even if there's less than 100 items, deque will handle the limit
        self.plot.plot(range(len(self.right_temperatures)), self.right_temperatures, label='Right Temperature', color='red')
        self.plot.plot(range(len(self.left_temperatures)), self.left_temperatures, label='Left Temperature', color='blue')

        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Temperature (°C)')
        if self.right_temperatures or self.left_temperatures:
            self.plot.legend(loc='upper left')

        self.canvas.draw_idle()
        self.after_id = self.master.after(1000, self.update_plot)  # Schedule next update

# Create the main window
root = tk.Tk()
app = SerialDataGUI(root)
root.mainloop()
