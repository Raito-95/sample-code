import tkinter as tk
from tkinter import ttk
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

class SerialReader:
    def __init__(self, port, baud_rate):
        self.serial_port = serial.Serial(port, baud_rate, timeout=1)
        self.running = False
        self.thread = None
        self.deques = {}
        self.callback = None

    def start_reading(self, callback):
        self.running = True
        self.callback = callback
        self.thread = threading.Thread(target=self.read_serial)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def read_serial(self):
        while self.running:
            try:
                line = self.serial_port.readline().decode("utf-8").rstrip()
                if line and self.callback:
                    self.callback(line)
                for pattern, deque_obj in self.deques.items():
                    regex = f"{pattern}:\\s*(-?\\d+\\.\\d+)"
                    match = re.search(regex, line)
                    if match:
                        deque_obj.append(float(match.group(1)))
            except serial.SerialException:
                break

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

    def send_command(self, command, add_newline):
        if self.serial_port and self.serial_port.is_open:
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
        self.pattern_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Status: Not connected")
        self.command_var = tk.StringVar()
        self.add_newline_var = tk.BooleanVar()
        self.last_update_time = time.time()
        self.user_scrolled = False
        self.setup_gui()

    def setup_gui(self):
        style = ttk.Style(self.master)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 12), padding=6)
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TCombobox', font=('Helvetica', 12))
        style.configure('TCheckbutton', font=('Helvetica', 12))
        style.configure('TFrame', padding=10)
        
        main_frame = ttk.Frame(self.master)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        connection_frame = ttk.LabelFrame(left_frame, text="Connection Settings")
        connection_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)

        port_label = ttk.Label(connection_frame, text="Port:")
        port_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(
            connection_frame, textvariable=self.port_var, state="readonly", width=15
        )
        self.port_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_button = ttk.Button(
            connection_frame, text="\u21BB", command=self.update_ports, width=3
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
            width=10
        )
        self.baud_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        command_frame = ttk.LabelFrame(left_frame, text="Send Command")
        command_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)
        command_entry_frame = ttk.Frame(command_frame)
        command_entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.command_entry = ttk.Entry(command_entry_frame, textvariable=self.command_var, width=30)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        self.newline_check = ttk.Checkbutton(
            command_entry_frame, text="Add \\r\\n", variable=self.add_newline_var
        )
        self.newline_check.pack(side=tk.LEFT, padx=5, pady=5)

        send_button = ttk.Button(
            command_entry_frame, text="Send", command=self.send_command, width=8
        )
        send_button.pack(side=tk.LEFT, padx=5, pady=5)

        received_frame = ttk.LabelFrame(left_frame, text="Received Data")
        received_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.received_text = tk.Text(received_frame, height=10, state="disabled", width=50, font=('Helvetica', 12))
        self.received_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.received_text_scroll = ttk.Scrollbar(received_frame, orient="vertical", command=self.received_text.yview)
        self.received_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.received_text.configure(yscrollcommand=self.received_text_scroll.set)

        self.received_text_scroll.bind("<Button-1>", self.on_scroll_start)
        self.received_text_scroll.bind("<ButtonRelease-1>", self.on_scroll_end)

        pattern_frame = ttk.LabelFrame(left_frame, text="Pattern Input")
        pattern_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)
        pattern_entry_frame = ttk.Frame(pattern_frame)
        pattern_entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        pattern_entry = ttk.Entry(pattern_entry_frame, textvariable=self.pattern_var, width=30)
        pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        submit_button = ttk.Button(
            pattern_entry_frame, text="Submit", command=self.submit_pattern, width=8
        )
        submit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pattern_listbox = tk.Listbox(pattern_frame, height=6, width=50, font=('Helvetica', 12))
        self.pattern_listbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        delete_button = ttk.Button(
            pattern_frame, text="Delete", command=self.delete_pattern, width=8
        )
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.start_button = ttk.Button(
            button_frame, text="Start", command=self.start_clicked, width=10
        )
        self.start_button.pack(
            side=tk.LEFT, padx=(10, 5), pady=5, fill=tk.BOTH, expand=True
        )

        self.stop_button = ttk.Button(
            button_frame, text="Stop", command=self.stop_clicked, state="disabled", width=10
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.clear_button = ttk.Button(
            button_frame, text="Clear", command=self.clear_all, width=10
        )
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.exit_button = ttk.Button(
            button_frame, text="Exit", command=self.master.destroy, width=10
        )
        self.exit_button.pack(
            side=tk.LEFT, padx=(5, 10), pady=5, fill=tk.BOTH, expand=True
        )

        status_bar = ttk.Label(
            left_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_ports()
        self.master.after(UPDATE_INTERVAL_MS, self.update_plot)

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
            self.serial_reader.start_reading(self.display_received_data)
            self.status_var.set(
                f"Connected to {self.port_var.get()} at {baud_rate} baud."
            )
            self.toggle_buttons(True)
        except serial.SerialException as e:
            self.status_var.set(f"Failed to connect: {str(e)}")
        except ValueError:
            self.status_var.set("Invalid baud rate.")

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
                self.status_var.set("Serial connection has been closed.")

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
            self.status_var.set("Pattern cannot be empty.")
            return

        try:
            re.compile(pattern)
        except re.error:
            self.status_var.set("The entered pattern is not a valid regular expression.")
            return

        if pattern in self.get_all_patterns():
            self.status_var.set("This pattern is already in the list.")
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
            self.schedule_plot_update()

    def clear_all(self):
        self.clear_plot()
        self.clear_received_data()

    def clear_plot(self):
        if self.serial_reader:
            self.serial_reader.reset_data()
        self.plot.clear()
        self.plot.set_xlabel("Data Point Index")
        self.plot.set_ylabel("Value")
        self.canvas.draw_idle()

    def clear_received_data(self):
        self.received_text.configure(state="normal")
        self.received_text.delete("1.0", tk.END)
        self.received_text.configure(state="disabled")

    def send_command(self):
        command = self.command_var.get()
        if len(command) > COMMAND_MAX_LENGTH:
            self.status_var.set("Command is too long.")
            return

        add_newline = self.add_newline_var.get()
        if self.serial_reader and self.serial_reader.is_connected():
            try:
                self.serial_reader.send_command(command, add_newline)
                self.status_var.set(f"Sent command: {command}")
            except serial.SerialException as e:
                self.status_var.set(f"Failed to send command: {str(e)}")
        else:
            self.status_var.set("Serial port is not connected.")

    def display_received_data(self, line):
        self.received_text.configure(state="normal")
        self.received_text.insert(tk.END, line + '\n')
        if not self.user_scrolled:
            self.received_text.yview(tk.END)
        self.received_text.configure(state="disabled")

    def on_scroll_start(self, event):
        self.user_scrolled = True

    def on_scroll_end(self, event):
        if self.received_text.yview()[1] == 1.0:
            self.user_scrolled = False

    def schedule_plot_update(self):
        self.master.after(UPDATE_INTERVAL_MS, self.update_plot)

    def update_plot(self):
        current_time = time.time()
        if current_time - self.last_update_time < UPDATE_INTERVAL_MS / 1000.0:
            self.schedule_plot_update()
            return

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
        self.last_update_time = current_time
        self.schedule_plot_update()

    def check_connection_periodically(self):
        if self.serial_reader and not self.serial_reader.is_connected():
            self.stop_clicked(show_message=False)
            self.status_var.set("The connection to the device has been lost.")
        self.master.after(1000, self.check_connection_periodically)

root = tk.Tk()
app = SerialDataApp(root)
root.mainloop()
