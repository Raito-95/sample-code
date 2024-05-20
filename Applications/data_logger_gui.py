import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import threading
import re
import serial

BUFFER_SIZE = 100
NUM_LINES_TO_READ = 1


class SerialReader:
    def __init__(self, port, baud_rate):
        self.serial_port = serial.Serial(port, baud_rate, timeout=1)
        self.running = False
        self.thread = None
        self.deques = {}

    def start_reading(self, callback):
        self.running = True
        self.thread = threading.Thread(target=self.read_serial, args=(callback,))
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def read_serial(self, callback):
        while self.running:
            line = self.serial_port.readline().decode("utf-8").rstrip()
            for pattern, deque_obj in self.deques.items():
                regex = f"{pattern}:\\s*(-?\\d+\\.\\d+)"
                match = re.search(regex, line)
                if match:
                    deque_obj.append(float(match.group(1)))
                    callback()

    def add_pattern(self, pattern):
        self.deques[pattern] = deque(maxlen=BUFFER_SIZE)

    def remove_pattern(self, pattern):
        if pattern in self.deques:
            del self.deques[pattern]

    def reset_data(self):
        for deque_obj in self.deques.values():
            deque_obj.clear()

    def is_connected(self) -> bool:
        return self.serial_port.is_open if self.serial_port else False


class SerialDataGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.serial_reader = None
        self.pattern_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Status: Not connected")
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        connection_frame = ttk.LabelFrame(
            main_frame, text="Connection Settings", padding="10"
        )
        connection_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        port_label = ttk.Label(connection_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(
            connection_frame, textvariable=self.port_var, state="readonly"
        )
        self.port_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_button = ttk.Button(
            connection_frame, text="\u21BB", command=self.update_ports
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        baud_label = ttk.Label(connection_frame, text="Baud Rate:")
        baud_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.baud_var = tk.StringVar(value="115200")
        self.baud_dropdown = ttk.Combobox(
            connection_frame,
            textvariable=self.baud_var,
            state="readonly",
            values=("9600", "19200", "38400", "57600", "115200"),
        )
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        pattern_frame = ttk.LabelFrame(main_frame, text="Pattern Input", padding="10")
        pattern_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        pattern_entry_frame = ttk.Frame(pattern_frame)
        pattern_entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        pattern_entry = ttk.Entry(pattern_entry_frame, textvariable=self.pattern_var)
        pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        submit_button = ttk.Button(
            pattern_entry_frame, text="Submit", command=self.submit_pattern
        )
        submit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pattern_listbox = tk.Listbox(pattern_frame, height=6)
        self.pattern_listbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        delete_button = ttk.Button(
            pattern_frame, text="Delete", command=self.delete_pattern
        )
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.start_button = ttk.Button(
            button_frame, text="Start", command=self.start_clicked
        )
        self.start_button.pack(
            side=tk.LEFT, padx=(10, 5), pady=5, fill=tk.BOTH, expand=True
        )

        self.stop_button = ttk.Button(
            button_frame, text="Stop", command=self.stop_clicked, state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.clear_button = ttk.Button(
            button_frame, text="Clear", command=self.clear_plot
        )
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.exit_button = ttk.Button(
            button_frame, text="Exit", command=self.master.destroy
        )
        self.exit_button.pack(
            side=tk.LEFT, padx=(5, 10), pady=5, fill=tk.BOTH, expand=True
        )

        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )

        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.update_ports()

    def update_ports(self):
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_dropdown["values"] = available_ports
        self.port_var.set(available_ports[0] if available_ports else "")

    def start_clicked(self):
        try:
            baud_rate = int(self.baud_var.get())
            if not self.serial_reader:
                self.serial_reader = SerialReader(self.port_var.get(), baud_rate)
                for pattern in self.get_all_patterns():
                    self.serial_reader.add_pattern(pattern)
            self.serial_reader.start_reading(self.update_plot)
            self.status_var.set(
                f"Connected to {self.port_var.get()} at {baud_rate} baud."
            )
            self.toggle_buttons(True)
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.status_var.set("Connection failed")
        except ValueError:
            messagebox.showerror("Configuration Error", "Invalid baud rate.")

    def get_all_patterns(self):
        return [
            self.pattern_listbox.get(idx) for idx in range(self.pattern_listbox.size())
        ]

    def stop_clicked(self, show_message=True):
        if self.serial_reader:
            self.serial_reader.stop_reading()
            self.serial_reader = None
            self.status_var.set("Disconnected.")
            self.toggle_buttons(False)
            if show_message:
                messagebox.showinfo(
                    "Disconnected", "Serial connection has been closed."
                )

    def toggle_buttons(self, is_running):
        state = "disabled" if is_running else "normal"
        self.port_dropdown["state"] = state
        self.baud_dropdown["state"] = state
        self.refresh_button["state"] = state
        self.start_button["state"] = state
        self.stop_button["state"] = "normal" if is_running else "disabled"
        self.clear_button["state"] = "normal"
        self.pattern_listbox["state"] = "normal"

    def submit_pattern(self):
        pattern = self.pattern_var.get()
        if not pattern:
            messagebox.showerror("Invalid Pattern", "Pattern cannot be empty.")
            return

        try:
            re.compile(pattern)
        except re.error:
            messagebox.showerror(
                "Invalid Pattern",
                "The entered pattern is not a valid regular expression.",
            )
            return

        if pattern in self.get_all_patterns():
            messagebox.showerror(
                "Duplicate Pattern", "This pattern is already in the list."
            )
            return

        self.pattern_listbox.insert(tk.END, pattern)
        if self.serial_reader:
            self.serial_reader.add_pattern(pattern)
        self.pattern_var.set("")

    def delete_pattern(self):
        selected_index = self.pattern_listbox.curselection()
        if selected_index:
            selected_pattern = self.pattern_listbox.get(selected_index)
            self.pattern_listbox.delete(selected_index)
            if self.serial_reader:
                self.serial_reader.remove_pattern(selected_pattern)
            self.update_plot()

    def clear_plot(self):
        if self.serial_reader:
            self.serial_reader.reset_data()
        self.plot.clear()
        self.plot.set_xlabel("Data Point Index")
        self.plot.set_ylabel("Value")
        self.canvas.draw_idle()

    def update_plot(self):
        if self.serial_reader:
            self.master.after(0, self.update_plot_main_thread)

    def update_plot_main_thread(self):
        if self.figure is None or self.plot is None:
            return

        self.plot.cla()

        data_plotted = False

        if self.serial_reader:
            for pattern, deque_obj in self.serial_reader.deques.items():
                if deque_obj:
                    x_values = range(1, len(deque_obj) + 1)
                    self.plot.plot(x_values, deque_obj, label=pattern)
                    data_plotted = True

        if data_plotted:
            self.plot.legend(loc="upper left")

        self.plot.set_xlabel("Data Point Index")
        self.plot.set_ylabel("Value")
        self.canvas.draw_idle()

    def check_connection_periodically(self):
        if self.serial_reader and not self.serial_reader.is_connected():
            self.stop_clicked(show_message=False)
            messagebox.showinfo(
                "Connection Lost", "The connection to the device has been lost."
            )
        self.master.after(1000, self.check_connection_periodically)


root = tk.Tk()
app = SerialDataGUI(root)
root.mainloop()
