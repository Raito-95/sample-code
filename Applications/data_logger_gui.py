# pylint: disable=all
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
from collections import deque

import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BUFFER_SIZE = 100  # Size of the data buffer
NUM_LINES_TO_READ = 2  # Number of lines to read from the serial port at a time


class SerialDataGUI(tk.Frame):
    """GUI for serial data communication and visualization."""

    def __init__(self, master: tk.Tk):
        """Initialize the GUI and set up the main interface."""
        super().__init__(master)
        self.master = master
        self.serial_port = None
        self.serial_thread = None
        self.running = False
        self.deques = {}
        self.pattern_var = tk.StringVar()
        self.pattern_listbox = tk.Listbox(self, height=6)
        self.setup_gui()

    def setup_gui(self):
        """Set up the main GUI layout, including connection settings and pattern input."""
        self.master.title('Serial Data GUI')
        self.master.resizable(False, False)

        # Main frame setup
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Connection settings frame
        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Port selection
        port_label = ttk.Label(connection_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(connection_frame, textvariable=self.port_var, state="readonly")
        self.port_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Refresh button
        refresh_text = "\u21BB"
        self.refresh_button = ttk.Button(connection_frame, text=refresh_text, command=self.update_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Baud rate selection
        baud_label = ttk.Label(connection_frame, text="Baud Rate:")
        baud_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_dropdown = ttk.Combobox(connection_frame, textvariable=self.baud_var, state="readonly")
        self.baud_dropdown['values'] = ("9600", "19200", "38400", "57600", "115200")
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Pattern input frame
        pattern_frame = ttk.LabelFrame(main_frame, text="Pattern Input", padding="10")
        pattern_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.setup_pattern_controls(pattern_frame)

        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicked)
        self.start_button.pack(side=tk.LEFT, padx=(10, 5), pady=5, fill=tk.BOTH, expand=True)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicked, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_plot)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.master.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=(5, 10), pady=5, fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Status: Not connected")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Plotting area
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_ports_periodically()

    def setup_pattern_controls(self, parent):
        """Set up controls for pattern input within the pattern frame."""
        pattern_entry_frame = ttk.Frame(parent)
        pattern_entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        pattern_entry = ttk.Entry(pattern_entry_frame, textvariable=self.pattern_var)
        pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        pattern_entry_tooltip = ttk.Label(pattern_entry_frame, text="Enter regex pattern here")
        pattern_entry_tooltip.pack(side=tk.LEFT, padx=5)

        submit_button = ttk.Button(pattern_entry_frame, text="Submit", command=self.submit_pattern)
        submit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pattern_listbox = tk.Listbox(parent, height=6)
        self.pattern_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_button = ttk.Button(parent, text="Delete", command=self.delete_pattern)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

    def update_ports(self):
        """Refresh the list of available serial ports."""
        if self.start_button['state'] == 'disabled':
            return  # Do nothing if the start button is disabled
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        self.port_dropdown['values'] = ports
        self.port_var.set(ports[0] if ports else '')

    def update_ports_periodically(self):
        """Periodically refresh the list of serial ports."""
        self.update_ports()
        self.after(5000, self.update_ports_periodically)

    def start_clicked(self):
        """Handle the start button click: open serial port and start reading."""
        try:
            baud_rate = int(self.baud_var.get())
            self.serial_port = serial.Serial(self.port_var.get(), baud_rate, timeout=1)
            self.status_var.set(f"Connected to {self.port_var.get()} at {baud_rate} baud.")
            self.running = True

            self.serial_thread = threading.Thread(target=self.read_serial)
            self.serial_thread.daemon = True
            self.serial_thread.start()

            self.update_plot()
        except serial.SerialException as e:
            messagebox.showerror("Serial Connection Error", str(e))
            self.status_var.set("Connection failed")
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid baud rate.")
            self.status_var.set("Invalid baud rate")

    def stop_clicked(self):
        """Handle the stop button click: close serial port and stop reading."""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.status_var.set("Disconnected.")

        # Reset UI elements to their default states
        self.port_dropdown['state'] = 'readonly'
        self.baud_dropdown['state'] = 'readonly'
        self.refresh_button['state'] = 'normal'
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'

    def submit_pattern(self):
        """Submit a new pattern for data extraction."""
        pattern = self.pattern_var.get()
        try:
            re.compile(pattern)  # Check if pattern is valid regex
            if pattern not in self.deques:
                self.deques[pattern] = deque(maxlen=BUFFER_SIZE)
                self.pattern_listbox.insert(tk.END, pattern)
            self.pattern_var.set('')
        except re.error:
            messagebox.showerror("Invalid Pattern", "The entered pattern is not a valid regular expression.")

    def delete_pattern(self):
        """Delete the selected pattern."""
        selected_index = self.pattern_listbox.curselection()
        if selected_index:
            selected_pattern = self.pattern_listbox.get(selected_index)
            self.pattern_listbox.delete(selected_index)
            del self.deques[selected_pattern]

    def read_serial(self):
        """Read data from the serial port and process it according to the defined patterns."""
        while self.running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    for _ in range(NUM_LINES_TO_READ):
                        line = self.serial_port.readline().decode('utf-8').rstrip()
                        for pattern, deque_obj in self.deques.items():
                            regex = f"{pattern}:\\s*(-?\\d+\\.\\d+)"
                            match = re.search(regex, line)
                            if match:
                                deque_obj.append(float(match.group(1)))
                except serial.SerialException as e:
                    messagebox.showerror("Serial Reading Error", str(e))

    def clear_plot(self):
        """Clear the plot area and reset data series."""
        for d in self.deques.values():
            d.clear()

        self.plot.clear()
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Value')
        self.canvas.draw_idle()

    def update_plot(self):
        """Update the plot with new data."""
        if self.running:
            self.plot.clear()

        # Track whether any data has been plotted
        data_plotted = False

        for pattern, deque_obj in self.deques.items():
            if deque_obj:
                self.plot.plot(range(len(deque_obj)), deque_obj, label=pattern)
                data_plotted = True  # Data has been plotted

        if data_plotted:
            self.plot.legend(loc='upper left')
        else:
            self.status_var.set("No data to display")

        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Value')
        self.canvas.draw_idle()
        self.master.after(1000, self.update_plot)


root = tk.Tk()
app = SerialDataGUI(root)
root.mainloop()