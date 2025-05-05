import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import threading
import re
import serial
import time

BUFFER_SIZE = 100
UPDATE_INTERVAL_MS = 1000
COMMAND_MAX_LENGTH = 100


class PatternManager:
    def __init__(self):
        self.patterns = []

    def add(self, pattern):
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def remove(self, pattern):
        if pattern in self.patterns:
            self.patterns.remove(pattern)

    def clear(self):
        self.patterns.clear()

    def get_all(self):
        return list(self.patterns)


class SerialReader:
    def __init__(self, port, baud_rate):
        self.running = False
        self.thread = None
        self.deques = {}
        self.callback = None

        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
        except serial.SerialException as e:
            self.serial_port = None
            raise e

    def start_reading(self, callback):
        if not self.serial_port or not self.serial_port.is_open:
            raise serial.SerialException("Serial port not available")
        self.running = True
        self.callback = callback
        self.thread = threading.Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def stop_reading(self):
        self.running = False
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
        except serial.SerialException as e:
            print(f"Error closing port: {e}")

    def read_serial(self):
        while self.running:
            try:
                line = self.serial_port.readline().decode("utf-8", errors="ignore").rstrip()
                if line and self.callback:
                    self.callback(line)
                for pattern, deque_obj in self.deques.items():
                    regex = f"{pattern}:\\s*(-?\\d+\\.\\d+)"
                    match = re.search(regex, line)
                    if match:
                        deque_obj.append(float(match.group(1)))
            except (serial.SerialException, OSError) as e:
                print(f"Serial read error: {e}")
                self.running = False
                break
            except Exception as e:
                print(f"Unexpected read error: {e}")

    def add_pattern(self, pattern):
        if pattern not in self.deques:
            self.deques[pattern] = deque(maxlen=BUFFER_SIZE)

    def remove_pattern(self, pattern):
        if pattern in self.deques:
            del self.deques[pattern]

    def reset_data(self):
        for deque_obj in self.deques.values():
            deque_obj.clear()

    def is_connected(self):
        return self.serial_port and self.serial_port.is_open

    def send_command(self, command, add_newline):
        if self.is_connected():
            if add_newline:
                command += '\r\n'
            self.serial_port.write(command.encode('utf-8'))
        else:
            raise serial.SerialException("Serial port is not open")


class SerialDataApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.serial_reader = None
        self.pattern_manager = PatternManager()
        self.pattern_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Status: Not connected")
        self.command_var = tk.StringVar()
        self.add_newline_var = tk.BooleanVar()
        self.last_update_time = time.time()
        self.user_scrolled = False
        self.setup_gui()
        self.master.after(1000, self.check_connection_periodically)
        
    def setup_gui(self):
        style = ttk.Style(self.master)
        style.theme_use('clam')

        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Connection Frame
        connection_frame = ttk.LabelFrame(left_frame, text="Connection Settings")
        connection_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(connection_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(connection_frame, textvariable=self.port_var, state="readonly", width=15)
        self.port_dropdown.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(connection_frame, text="\u21BB", command=self.update_ports, width=3)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        ttk.Label(connection_frame, text="Baud Rate:").pack(side=tk.LEFT, padx=5)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_dropdown = ttk.Combobox(
            connection_frame,
            textvariable=self.baud_var,
            state="readonly",
            values=(
                "110", "300", "600", "1200", "2400",
                "4800", "9600", "14400", "19200", "28800",
                "38400", "57600", "76800", "115200", "128000", "230400", "256000", "460800", "921600"
            ),
            width=10
        )
        self.baud_dropdown.pack(side=tk.LEFT, padx=5)

        # Command Frame
        command_frame = ttk.LabelFrame(left_frame, text="Send Command")
        command_frame.pack(fill=tk.X, padx=5, pady=5)

        command_entry = ttk.Entry(command_frame, textvariable=self.command_var, width=30)
        command_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        ttk.Checkbutton(command_frame, text="Add \\r\\n", variable=self.add_newline_var).pack(side=tk.LEFT)
        ttk.Button(command_frame, text="Send", command=self.send_command).pack(side=tk.LEFT, padx=5)

        # Received Data
        received_frame = ttk.LabelFrame(left_frame, text="Received Data")
        received_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.received_text = tk.Text(received_frame, height=10, state="disabled", width=50)
        self.received_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(received_frame, command=self.received_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.received_text.config(yscrollcommand=scroll.set)
        scroll.bind("<Button-1>", self.on_scroll_start)
        scroll.bind("<ButtonRelease-1>", self.on_scroll_end)

        # Pattern Management
        pattern_frame = ttk.LabelFrame(left_frame, text="Pattern Input")
        pattern_frame.pack(fill=tk.X, padx=5, pady=5)

        pattern_entry_frame = ttk.Frame(pattern_frame)
        pattern_entry_frame.pack(fill=tk.X, padx=5, pady=5)

        pattern_entry = ttk.Entry(pattern_entry_frame, textvariable=self.pattern_var, width=30)
        pattern_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(pattern_entry_frame, text="Submit", command=self.submit_pattern).pack(side=tk.LEFT, padx=5)

        pattern_list_frame = ttk.Frame(pattern_frame)
        pattern_list_frame.pack(fill=tk.X, padx=5, pady=5)

        self.pattern_listbox = tk.Listbox(pattern_list_frame, height=6, width=50)
        self.pattern_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Button(pattern_list_frame, text="Delete", command=self.delete_pattern).pack(side=tk.LEFT, padx=5)

        # Control Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicked)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicked, state="disabled")
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.master.destroy)
        self.exit_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Status Bar
        ttk.Label(left_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)

        # Plotting
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_ports()
        self.master.after(UPDATE_INTERVAL_MS, self.update_plot)

    def update_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_dropdown["values"] = ports
        self.port_var.set(ports[0] if ports else "")

    def start_clicked(self):
        if self.serial_reader:
            self.serial_reader.stop_reading()
            self.serial_reader = None

        try:
            baud = int(self.baud_var.get())
            self.serial_reader = SerialReader(self.port_var.get(), baud)
            for pattern in self.pattern_manager.get_all():
                self.serial_reader.add_pattern(pattern)
            self.serial_reader.start_reading(self.display_received_data)
            self.status_var.set(f"Connected to {self.port_var.get()} at {baud} baud.")
            self.toggle_buttons(True)
        except Exception as e:
            self.status_var.set(f"Failed to connect: {e}")
            messagebox.showerror("Connection Error", str(e))

    def stop_clicked(self):
        if self.serial_reader:
            self.serial_reader.stop_reading()
            self.serial_reader = None
        self.status_var.set("Disconnected.")
        self.toggle_buttons(False)

    def toggle_buttons(self, is_running):
        state = "disabled" if is_running else "normal"
        self.port_dropdown["state"] = state
        self.baud_dropdown["state"] = state
        self.refresh_button["state"] = state
        self.start_button["state"] = state
        self.stop_button["state"] = "normal" if is_running else "disabled"

    def submit_pattern(self):
        pattern = self.pattern_var.get()
        if not pattern:
            self.status_var.set("Pattern cannot be empty.")
            return
        try:
            re.compile(pattern)
        except re.error:
            self.status_var.set("Invalid regular expression.")
            return
        if pattern in self.pattern_manager.get_all():
            self.status_var.set("Pattern already exists.")
            return
        self.pattern_listbox.insert(tk.END, pattern)
        self.pattern_manager.add(pattern)
        if self.serial_reader:
            self.serial_reader.add_pattern(pattern)
        self.pattern_var.set("")

    def delete_pattern(self):
        selected = self.pattern_listbox.curselection()
        if selected:
            pattern = self.pattern_listbox.get(selected)
            self.pattern_listbox.delete(selected)
            self.pattern_manager.remove(pattern)
            if self.serial_reader:
                self.serial_reader.remove_pattern(pattern)

    def clear_all(self):
        self.clear_received_data()
        self.clear_plot()

    def clear_received_data(self):
        self.received_text.configure(state="normal")
        self.received_text.delete("1.0", tk.END)
        self.received_text.configure(state="disabled")

    def clear_plot(self):
        if self.serial_reader:
            self.serial_reader.reset_data()
        self.plot.clear()
        self.plot.set_xlabel("Data Point Index")
        self.plot.set_ylabel("Value")
        self.canvas.draw_idle()

    def send_command(self):
        command = self.command_var.get()
        if len(command) > COMMAND_MAX_LENGTH:
            self.status_var.set("Command too long.")
            return
        try:
            if self.serial_reader and self.serial_reader.is_connected():
                self.serial_reader.send_command(command, self.add_newline_var.get())
                self.status_var.set(f"Sent command: {command}")
            else:
                self.status_var.set("Serial not connected.")
        except serial.SerialException as e:
            self.status_var.set(f"Send failed: {e}")

    def display_received_data(self, line):
        self.received_text.configure(state="normal")
        self.received_text.insert(tk.END, line + '\n')
        if not self.user_scrolled:
            self.received_text.yview(tk.END)
        self.received_text.configure(state="disabled")

    def on_scroll_start(self, _):
        self.user_scrolled = True

    def on_scroll_end(self, _):
        if self.received_text.yview()[1] == 1.0:
            self.user_scrolled = False

    def update_plot(self):
        if not self.serial_reader:
            self.schedule_plot_update()
            return
        self.plot.cla()
        plotted = False
        for pattern, data in self.serial_reader.deques.items():
            if data:
                self.plot.plot(range(len(data)), data, label=pattern)
                plotted = True
        if plotted:
            self.plot.legend(loc="upper left")
        self.plot.set_xlabel("Data Point Index")
        self.plot.set_ylabel("Value")
        self.canvas.draw_idle()
        self.schedule_plot_update()

    def schedule_plot_update(self):
        self.master.after(UPDATE_INTERVAL_MS, self.update_plot)

    def check_connection_periodically(self):
        if self.serial_reader and not self.serial_reader.is_connected():
            self.stop_clicked()
            self.status_var.set("Connection lost.")
        self.master.after(1000, self.check_connection_periodically)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Serial Monitor with Live Plot")
    app = SerialDataApp(root)
    root.mainloop()
