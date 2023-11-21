import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re
import serial
from collections import deque

BUFFER_SIZE = 100 # Buffer size for data storage
NUM_LINES_TO_READ = 2 # Number of lines to read from serial at once

class SerialDataGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.serial_port = None
        self.after_id = None
        self.deques = {} # Store data based on user-defined patterns
        self.setup_gui()

    # Setup main GUI layout
    # Includes connection settings, pattern input, and control buttons
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

        refresh_text = "\u21BB"
        self.refresh_button = ttk.Button(connection_frame, text=refresh_text, command=self.update_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        baud_label = ttk.Label(connection_frame, text="Baud Rate:")
        baud_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_dropdown = ttk.Combobox(connection_frame, textvariable=self.baud_var, state="readonly")
        self.baud_dropdown['values'] = ("9600", "19200", "38400", "57600", "115200")
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        pattern_frame = ttk.LabelFrame(main_frame, text="Pattern Input", padding="10")
        pattern_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.setup_pattern_controls(pattern_frame)

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

    # Setup controls for pattern input and management
    def setup_pattern_controls(self, parent):
        pattern_entry_frame = ttk.Frame(parent)
        pattern_entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.pattern_var = tk.StringVar()
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

    # Refresh list of available serial ports
    def update_ports(self):
        if self.start_button['state'] == 'disabled':
            return
        current_port = self.port_var.get()
        ports = [comport.device for comport in serial.tools.list_ports.comports()]
        self.port_dropdown['values'] = ports
        if current_port in ports:
            self.port_var.set(current_port)
        elif ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set('')

    # Periodically update the list of available serial ports
    def update_ports_periodically(self):
        self.update_ports()
        self.after(5000, self.update_ports_periodically)

    # Handles starting the serial communication with the specified port and baud rate
    def start_clicked(self):
        try:
            baud_rate = int(self.baud_var.get())  # Parse baud rate from user input
            # Attempt to open the serial port with the specified baud rate
            self.serial_port = serial.Serial(self.port_var.get(), baud_rate, timeout=1)
            self.status_var.set(f"Connected to {self.port_var.get()} at {baud_rate} baud.")
            
            # Disable UI elements to prevent changes during active connection
            self.port_dropdown['state'] = 'disabled'
            self.baud_dropdown['state'] = 'disabled'
            self.refresh_button['state'] = 'disabled'
            
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'
            self.update_plot()
        except serial.SerialException as e:
            messagebox.showerror("Serial Connection Error", str(e))
            self.status_var.set("Connection failed")
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid baud rate.")
            self.status_var.set("Invalid baud rate")

    # Handle stopping serial communication
    def stop_clicked(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.status_var.set("Disconnected.")
            except serial.SerialException as e:
                messagebox.showerror("Serial Disconnection Error", str(e))
                self.status_var.set("Disconnection failed")
        else:
            self.status_var.set("No active connection")

        self.port_dropdown['state'] = 'readonly'
        self.baud_dropdown['state'] = 'readonly'
        self.refresh_button['state'] = 'normal'
        
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'

    # Validate and submit user-entered pattern for data extraction
    def submit_pattern(self):
        pattern = self.pattern_var.get()
        try:
            re.compile(pattern)
            if pattern not in self.deques:
                self.deques[pattern] = deque(maxlen=BUFFER_SIZE)
                self.pattern_listbox.insert(tk.END, pattern)
            self.pattern_var.set('')
        except re.error:
            messagebox.showerror("Invalid Pattern", "The entered pattern is not a valid regular expression.")

    # Delete a selected pattern
    def delete_pattern(self):
        selected_index = self.pattern_listbox.curselection()
        if selected_index:
            selected_pattern = self.pattern_listbox.get(selected_index)
            self.pattern_listbox.delete(selected_index)
            del self.deques[selected_pattern]

    # Read and process serial data based on defined patterns
    def read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                for _ in range(NUM_LINES_TO_READ):
                    line = self.serial_port.readline().decode('utf-8').rstrip()
                    for pattern, deque_obj in self.deques.items():
                        regex = f"{pattern}:\s*(-?\d+\.\d+)"
                        match = re.search(regex, line)
                        if match and match.group(1):
                            try:
                                deque_obj.append(float(match.group(1)))
                            except ValueError:
                                pass
            except serial.SerialException as e:
                messagebox.showerror("Serial Reading Error", str(e))

    # Clear data and reset plot
    def clear_plot(self):
        for deque in self.deques.values():
            deque.clear()

        self.plot.clear()
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Value')
        self.canvas.draw_idle()

    # Processes incoming serial data and updates the plot with new values
    def update_plot(self):
        self.read_serial()  # Read new data from the serial port
        self.plot.clear()   # Clear the existing plot

        # Plot new data for each user-defined pattern
        for pattern, deque_obj in self.deques.items():
            if deque_obj:
                # Plot data with a label for the legend
                self.plot.plot(range(len(deque_obj)), deque_obj, label=pattern)

        # Display legend if there are any plotted data series
        if self.deques:
            self.plot.legend(loc='upper left')
        else:
            self.status_var.set("No data to display")

        # Set labels for the axes
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Value')
        self.canvas.draw_idle()
        # Schedule the next update
        self.after_id = self.master.after(1000, self.update_plot)


# Create and run the main application window
root = tk.Tk()
app = SerialDataGUI(root)
root.mainloop()
