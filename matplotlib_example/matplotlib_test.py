import serial  # 引用pySerial模組
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plot
import tkinter as tk
import datetime
import time
from collections import deque


first_data_time = datetime.datetime.now()
time_threshold = datetime.timedelta(seconds=300)
filename = f"data_{first_data_time.strftime('%Y%m%d%H%M%S')}.txt"


def exponential_smoothing(data, alpha=0.2):
    smoothed_data = [data[0]]
    for i in range(1, len(data)):
        smoothed_value = alpha * data[i] + (1 - alpha) * smoothed_data[i-1]
        smoothed_data.append(smoothed_value)
    return smoothed_data


def save_data_to_txt(data):
    global filename  # 將 filename 設定為全域變數

    with open(filename, 'a') as file:
        file.write(data + '\n')


class SerialSettings:
    def __init__(self, master):
        # 建立主視窗
        self.master = master
        self.master.title('GUI')
        self.master.resizable(False, False)
        self.is_running = False
        
        # 建立串口選擇標籤和下拉選單
        tk.Label(self.master, text="Port:").grid(row=0, column=0, sticky="E", pady=(10, 0))
        self.port_var = tk.StringVar()
        self.port_dropdown = tk.OptionMenu(self.master, self.port_var, *self.get_available_ports())
        self.port_dropdown.grid(row=0, column=1, sticky="N", pady=(10, 0))
        
        # 建立波特率標籤和下拉選單
        tk.Label(self.master, text="Baud Rate:").grid(row=1, column=0, sticky="E", pady=(10, 0))
        self.baud_var = tk.StringVar()
        self.baud_dropdown = tk.OptionMenu(self.master, self.baud_var, "115200")
        self.baud_dropdown.grid(row=1, column=1, sticky="N", pady=(10, 0))
        
        # 建立"Start"按鈕
        self.start_button = tk.Button(self.master, text="Start", command=self.ok_clicked)
        self.start_button.grid(row=0, column=2, sticky="N", pady=(10, 0))
        # 建立"Stop"按鈕
        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop_clicked)
        self.stop_button.grid(row=1, column=2, sticky="N", pady=(10, 0))

        # 建立狀態標籤
        self.status_label = tk.Label(self.master, text="Status: Not connected.")
        self.status_label.grid(row=2, column=0, columnspan=3, sticky="N", pady=(10, 0))

        self.frame_count = 0

    def get_available_ports(self):
        # 獲取所有可用的串口
        ports = serial.tools.list_ports.comports()
        port_list = []
        
        # 遍歷所有可用串口
        for port, desc, hwid in sorted(ports):
            # 檢查串口描述是否包含"USB"或"COM"
            if "USB" in desc or "COM" in desc:
                port_list.append(port)
        
        return port_list
    
    def ok_clicked(self):
        # 獲取選中的串口和波特率
        selected_port = self.port_var.get()
        selected_baud = int(self.baud_var.get())
        
        # 處理選中的串口和波特率
        print(f"Selected port: {selected_port}, baud rate: {selected_baud}")
        
        COM_PORT = str(selected_port)
        BAUD_RATES = str(selected_baud)
        ser = serial.Serial(COM_PORT, BAUD_RATES)

        buff = [deque([], maxlen=max_length) for _ in range(3)]

        self.is_running = True

        # 更新狀態標籤為已連接
        self.status_label["text"] = f"Status: Connected to {selected_port}"

        try:
            plot.ion()
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
            plot.ioff()

        # 關閉圖表視窗
        plot.close()

        # 關閉串口
        ser.close()

        # 更新狀態標籤
        self.status_label["text"] = f"Status: Disconnected {selected_port}"

        # 關閉視窗
        self.master.destroy()

    def stop_clicked(self):
        # 清除運行標誌
        self.is_running = False
    
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

    def draw_plots(self, buff):
        plot.clf()

        # 繪製 rightOrigVolt1 和 rightOrigVolt2 的圖表
        plot.subplot(2, 1, 1)
        buff_arr1 = np.array(list(buff[0]))
        buff_arr2 = np.array(list(buff[1]))
        plot.plot(buff_arr1, color='y', label='Volt1')
        plot.plot(buff_arr2, color='m', label='Volt2')
        plot.title('Voltage')
        plot.xlabel('Signal')
        plot.ylabel('Voltage')
        plot.grid(True)
        plot.ylim(0.9, 2.2)
        plot.legend(loc='upper left')

        # 標註 Volt1 和 Volt2 的最新值
        if len(buff[0]) > 1 and len(buff[1]) > 1:
            latest_value0 = buff_arr1[-1]
            latest_value1 = buff_arr2[-1]
            plot.annotate(f'{latest_value0:.3f}', (len(buff_arr1)-1, latest_value0),
                        xytext=(-10, 10), textcoords='offset points', color='y')
            plot.annotate(f'{latest_value1:.3f}', (len(buff_arr2)-1, latest_value1),
                        xytext=(-10, 10), textcoords='offset points', color='m')

        # 平滑 buff[2] 中的數據
        if len(buff[2]) > 0:
            smoothed_buff = exponential_smoothing(buff[2])
        else:
            smoothed_buff = buff[2]

        # 繪製原始和平滑的數據
        plot.subplot(2, 1, 2)
        buff_arr3 = np.array(buff[2])
        smoothed_buff_arr = np.array(smoothed_buff)
        plot.plot(smoothed_buff_arr, color='c', label='Smoothed')
        plot.plot(buff_arr3, color='lightgray', linestyle='--', label='Original')
        plot.title('Temperature')
        plot.xlabel('Signal')
        plot.ylabel('Temperature')
        plot.grid(True)
        plot.ylim(30, 110)
        plot.legend(loc='upper left')

        # 標註最新的溫度值
        if len(smoothed_buff) > 1:
            latest_value2 = smoothed_buff_arr[-1]
            plot.annotate(f'{latest_value2:.2f}', (len(smoothed_buff_arr)-1, latest_value2),
                        xytext=(-10, 10), textcoords='offset points', color='c')
            self.frame_count+=1
            if self.frame_count % 5 == 0:
                save_date = f'{latest_value2:.2f}'
                save_data_to_txt(save_date)
                self.frame_count = 0

        plot.subplots_adjust(hspace=0.5)

        plot.draw()
        plot.pause(0.1)

max_length = 100

# 建立主視窗
root = tk.Tk()

# 建立 SerialSettings 物件
serial_settings = SerialSettings(root)

# 開始主事件循環
root.mainloop()
