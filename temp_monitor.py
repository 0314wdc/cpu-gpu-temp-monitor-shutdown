import clr
import os
import sys
import threading
import time
import ctypes
import json
import tkinter as tk
from tkinter import ttk

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.json")

# 默认配置
default_config = {
    "target_cpu_temp": 65.0,
    "target_gpu_temp": 60.0,
    "shutdown_delay_minutes": 14,
    "check_interval": 4,
    "timer_shutdown_minutes": 10,
    "timer_start_check_minutes": 5,
    "active_tab": "monitor"  # 保存当前激活的导航栏选项
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # 以管理员权限重新运行脚本
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit(0)

# 加载OpenHardwareMonitor DLL
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OpenHardwareMonitorLib.dll")
clr.AddReference(dll_path)
from OpenHardwareMonitor.Hardware import Computer

computer = Computer()
computer.CPUEnabled = True
computer.GPUEnabled = True
computer.Open()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 检查类型和内容完整性
        if not isinstance(config, dict):
            raise ValueError("配置文件内容不是字典类型")
        # 检查所有key和类型
        changed = False
        for k, v in default_config.items():
            if k not in config or not isinstance(config[k], type(v)):
                config[k] = v
                changed = True
        # 移除多余的key
        extra_keys = [k for k in config if k not in default_config]
        if extra_keys:
            for k in extra_keys:
                del config[k]
            changed = True
        if changed:
            save_config(config)
        return config
    except Exception as e:
        print("读取配置失败，恢复默认:", e)
        save_config(default_config)
        return default_config.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("保存配置失败:", e)

config = load_config()

def read_temps():
    cpu_temps = []
    gpu_temps = []
    try:
        for hw in computer.Hardware:
            hw.Update()
            for sensor in hw.Sensors:
                if sensor.SensorType.ToString() == "Temperature" and sensor.Value is not None:
                    val = float(sensor.Value)
                    name = sensor.Name.lower()
                    hw_name = hw.Name.lower()
                    if "cpu" in hw_name or "cpu" in name:
                        cpu_temps.append(val)
                    elif "gpu" in hw_name or "gpu" in name or "vga" in hw_name:
                        gpu_temps.append(val)
    except Exception as e:
        print("读取温度异常:", e)
    cpu_temp = max(cpu_temps) if cpu_temps else 0.0
    gpu_temp = max(gpu_temps) if gpu_temps else 0.0
    return cpu_temp, gpu_temp

def do_shutdown():
    shutdown_window = tk.Tk()
    shutdown_window.title("小哈哈-关机倒计时")
    shutdown_window.geometry("300x150")

    countdown_label = ttk.Label(shutdown_window, text="14秒后关机", font=("Arial", 12))
    countdown_label.pack(pady=20)

    cancel_button = ttk.Button(shutdown_window, text="取消关机", command=lambda: cancel_shutdown(shutdown_window))
    cancel_button.pack(pady=10)

    def update_countdown(seconds_left):
        if seconds_left > 0:
            countdown_label.config(text=f"{seconds_left}秒后关机")
            shutdown_window.after(1000, update_countdown, seconds_left - 1)
        else:
            shutdown_window.destroy()
            try:
                os.system("shutdown /s /t 0")
            except Exception as e:
                print("关机命令执行失败:", e)

    def cancel_shutdown(window):
        window.destroy()

    shutdown_window.protocol("WM_DELETE_WINDOW", lambda: cancel_shutdown(shutdown_window))
    update_countdown(14)
    shutdown_window.mainloop()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("小哈哈-CPU/GPU温度监控与自动关机系统")
        self.geometry("500x380")
        self.resizable(True, True)

        self.cpu_temp = 0.0
        self.gpu_temp = 0.0

        # 状态变量
        self.shutdown_seconds_left = 0
        self.shutdown_timer_running = False

        self.check_delay_seconds_left = 0
        self.check_delay_timer_running = False

        self.monitor_thread = None
        self.monitor_thread_running = False

        # 从配置文件读取上次的导航栏选项，默认为monitor
        self.mode = config.get("active_tab", "monitor")  # monitor / timer_shutdown / timer_check

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 在创建UI组件后立即根据配置文件切换到上次激活的界面
        self.switch_mode(self.mode)
        self.update_ui() # 立即更新UI以显示初始状态

        # 启动温度监控线程
        self.start_monitoring()
        
        self.after(500, self.update_ui) # 周期性更新

    def create_widgets(self):
        # 顶部导航栏按钮
        nav_frame = ttk.Frame(self)
        nav_frame.pack(pady=5)

        self.btn_monitor = ttk.Button(nav_frame, text="温度监控", command=lambda: self.switch_mode("monitor"))
        self.btn_monitor.grid(row=0, column=0, padx=5)

        self.btn_timer_shutdown = ttk.Button(nav_frame, text="定时关机", command=lambda: self.switch_mode("timer_shutdown"))
        self.btn_timer_shutdown.grid(row=0, column=1, padx=5)

        self.btn_timer_check = ttk.Button(nav_frame, text="定时检测", command=lambda: self.switch_mode("timer_check"))
        self.btn_timer_check.grid(row=0, column=2, padx=5)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 温度监控界面
        self.frame_monitor = ttk.Frame(self.content_frame)
        self.cpu_label = ttk.Label(self.frame_monitor, text="CPU温度: -- ℃", font=("Arial", 14))
        self.cpu_label.pack(pady=10)

        self.gpu_label = ttk.Label(self.frame_monitor, text="GPU温度: -- ℃", font=("Arial", 14))
        self.gpu_label.pack(pady=10)

        self.temp_threshold_frame = ttk.Frame(self.frame_monitor)
        self.temp_threshold_frame.pack(pady=10)

        ttk.Label(self.temp_threshold_frame, text="目标CPU温度阈值 (℃)").grid(row=0, column=0, sticky="w")
        self.entry_cpu_threshold = ttk.Entry(self.temp_threshold_frame, width=10)
        self.entry_cpu_threshold.grid(row=0, column=1)
        self.entry_cpu_threshold.insert(0, str(config["target_cpu_temp"]))
        self.entry_cpu_threshold.bind("<FocusOut>", lambda e: self.save_threshold("target_cpu_temp", self.entry_cpu_threshold.get()))

        ttk.Label(self.temp_threshold_frame, text="目标GPU温度阈值 (℃)").grid(row=1, column=0, sticky="w")
        self.entry_gpu_threshold = ttk.Entry(self.temp_threshold_frame, width=10)
        self.entry_gpu_threshold.grid(row=1, column=1)
        self.entry_gpu_threshold.insert(0, str(config["target_gpu_temp"]))
        self.entry_gpu_threshold.bind("<FocusOut>", lambda e: self.save_threshold("target_gpu_temp", self.entry_gpu_threshold.get()))
        
        ttk.Label(self.temp_threshold_frame, text="关机倒计时(分钟)").grid(row=2, column=0, sticky="w")
        self.entry_shutdown_delay = ttk.Entry(self.temp_threshold_frame, width=10)
        self.entry_shutdown_delay.grid(row=2, column=1)
        self.entry_shutdown_delay.insert(0, str(config["shutdown_delay_minutes"]))
        self.entry_shutdown_delay.bind("<FocusOut>", lambda e: self.save_config_val("shutdown_delay_minutes", self.entry_shutdown_delay.get()))
        
        ttk.Label(self.temp_threshold_frame, text="检测间隔(秒)").grid(row=3, column=0, sticky="w")
        self.entry_check_interval = ttk.Entry(self.temp_threshold_frame, width=10)
        self.entry_check_interval.grid(row=3, column=1)
        self.entry_check_interval.insert(0, str(config["check_interval"]))
        self.entry_check_interval.bind("<FocusOut>", lambda e: self.save_config_val("check_interval", self.entry_check_interval.get()))

        self.label_monitor_status = ttk.Label(self.frame_monitor, text="", foreground="red", font=("Arial", 12))
        self.label_monitor_status.pack(pady=10)

        self.btn_stop_monitor = ttk.Button(self.frame_monitor, text="停止监控", command=self.stop_monitoring)
        self.btn_stop_monitor.pack(pady=5)
        # 移除初始pack，由switch_mode处理显示

        # 定时关机界面
        self.frame_timer_shutdown = ttk.Frame(self.content_frame)
        ttk.Label(self.frame_timer_shutdown, text="多少分钟后关机:").pack(pady=5)
        self.entry_shutdown_minutes = ttk.Entry(self.frame_timer_shutdown, width=10)
        self.entry_shutdown_minutes.pack(pady=5)
        self.entry_shutdown_minutes.insert(0, str(config["timer_shutdown_minutes"]))
        self.entry_shutdown_minutes.bind("<FocusOut>", lambda e: self.save_config_val("timer_shutdown_minutes", self.entry_shutdown_minutes.get()))

        self.label_shutdown_countdown = ttk.Label(self.frame_timer_shutdown, text="", font=("Arial", 12), foreground="red")
        self.label_shutdown_countdown.pack(pady=10)

        self.btn_start_shutdown = ttk.Button(self.frame_timer_shutdown, text="开始倒计时关机", command=self.start_shutdown_timer)
        self.btn_start_shutdown.pack(pady=5)

        self.btn_cancel_shutdown = ttk.Button(self.frame_timer_shutdown, text="取消倒计时", command=self.cancel_shutdown_timer)
        self.btn_cancel_shutdown.pack(pady=5)

        # 定时检测界面
        self.frame_timer_check = ttk.Frame(self.content_frame)
        ttk.Label(self.frame_timer_check, text="多少分钟后开始温度检测:").pack(pady=5)
        self.entry_check_minutes = ttk.Entry(self.frame_timer_check, width=10)
        self.entry_check_minutes.pack(pady=5)
        self.entry_check_minutes.insert(0, str(config["timer_start_check_minutes"]))
        self.entry_check_minutes.bind("<FocusOut>", lambda e: self.save_config_val("timer_start_check_minutes", self.entry_check_minutes.get()))

        self.label_check_countdown = ttk.Label(self.frame_timer_check, text="", font=("Arial", 12), foreground="blue")
        self.label_check_countdown.pack(pady=10)

        self.btn_start_check = ttk.Button(self.frame_timer_check, text="开始倒计时检测", command=self.start_check_timer)
        self.btn_start_check.pack(pady=5)

        self.btn_cancel_check = ttk.Button(self.frame_timer_check, text="取消倒计时", command=self.cancel_check_timer)
        self.btn_cancel_check.pack(pady=5)

    def save_threshold(self, key, val_str):
        try:
            val = float(val_str)
            config[key] = val
            save_config(config)
        except Exception as e:
            print(f"保存阈值失败: {e}")

    def save_config_val(self, key, val_str):
        try:
            val = int(val_str)
            config[key] = val
            save_config(config)
            # 如果修改的是检测间隔，立即更新监控线程
            if key == "check_interval" and self.monitor_thread_running:
                pass
        except Exception as e:
            print(f"保存配置失败: {e}")

    def save_config(self, config):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("保存配置失败:", e)

    def switch_mode(self, mode):
        # 切换模式前取消所有倒计时
        self.cancel_shutdown_timer()
        self.cancel_check_timer()
        
        self.mode = mode
        
        # 保存当前激活的导航栏选项
        config["active_tab"] = mode
        save_config(config)
        
        # 隐藏所有内容框架
        self.frame_monitor.pack_forget()
        self.frame_timer_shutdown.pack_forget()
        self.frame_timer_check.pack_forget()

        # 显示选定的内容框架
        if mode == "monitor":
            self.frame_monitor.pack(fill="both", expand=True)
        elif mode == "timer_shutdown":
            self.frame_timer_shutdown.pack(fill="both", expand=True)
            # 自动开始倒计时
            if not self.shutdown_timer_running:
                self.start_shutdown_timer()
        elif mode == "timer_check":
            self.frame_timer_check.pack(fill="both", expand=True)
            # 自动开始倒计时
            if not self.check_delay_timer_running:
                self.start_check_timer()

    def start_monitoring(self):
        if self.monitor_thread_running:
            return
        self.monitor_thread_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitor_thread_running = False
        self.label_monitor_status.config(text="监控已停止。")

    def monitor_loop(self):
        try:
            while self.monitor_thread_running:
                cpu, gpu = read_temps()
                self.cpu_temp = cpu
                self.gpu_temp = gpu

                # 温度低于阈值时触发关机倒计时（这里示例阈值是低于目标值，用户可改）
                if (cpu < config["target_cpu_temp"] and gpu < config["target_gpu_temp"]) and not self.shutdown_timer_running:
                    self.start_shutdown_timer(auto=True)

                time.sleep(config.get("check_interval", 4))
        except Exception as e:
            print("监控线程异常:", e)

    def start_shutdown_timer(self, auto=False):
        if self.shutdown_timer_running:
            # 已经有倒计时，不重复启动
            return
        try:
            if auto:
                delay = config.get("shutdown_delay_minutes", 14)
            else:
                delay = int(self.entry_shutdown_minutes.get())
                config["timer_shutdown_minutes"] = delay
                save_config(config)
            self.shutdown_seconds_left = delay * 60
            self.shutdown_timer_running = True
            self.update_shutdown_countdown()
            
            # 确保温度监控继续运行
            if not self.monitor_thread_running:
                self.start_monitoring()
                
            # 更新状态显示
            if hasattr(self, 'label_monitor_status'):
                self.label_monitor_status.config(text="关机倒计时开始...")
        except Exception as e:
            print("启动关机倒计时失败:", e)

    def update_shutdown_countdown(self):
        if self.shutdown_timer_running and self.shutdown_seconds_left > 0:
            mins, secs = divmod(self.shutdown_seconds_left, 60)
            self.label_shutdown_countdown.config(text=f"关机倒计时：{mins}分{secs}秒")
            self.shutdown_seconds_left -= 1
            self.after(1000, self.update_shutdown_countdown)
        elif self.shutdown_timer_running and self.shutdown_seconds_left <= 0:
            self.label_shutdown_countdown.config(text="即将关机...")
            do_shutdown()
        else:
            self.label_shutdown_countdown.config(text="")
            self.shutdown_timer_running = False

    def cancel_shutdown_timer(self):
        if self.shutdown_timer_running:
            self.shutdown_timer_running = False
            self.shutdown_seconds_left = 0
            self.label_shutdown_countdown.config(text="倒计时已取消。")
            self.label_monitor_status.config(text="")

    def start_check_timer(self):
        if self.check_delay_timer_running:
            return
        try:
            mins = int(self.entry_check_minutes.get())
            config["timer_start_check_minutes"] = mins
            save_config(config)
            self.check_delay_seconds_left = mins * 60
            self.check_delay_timer_running = True
            # 立即更新倒计时显示
            mins, secs = divmod(self.check_delay_seconds_left, 60)
            self.label_check_countdown.config(text=f"距离温度检测开始还有 {mins}分{secs}秒")
            self.update_check_countdown()
        except Exception as e:
            print("启动检测倒计时失败:", e)

    def update_check_countdown(self):
        if self.check_delay_timer_running and self.check_delay_seconds_left > 0:
            mins, secs = divmod(self.check_delay_seconds_left, 60)
            self.label_check_countdown.config(text=f"距离温度检测开始还有 {mins}分{secs}秒")
            self.check_delay_seconds_left -= 1
            self.after(1000, self.update_check_countdown)
        elif self.check_delay_timer_running and self.check_delay_seconds_left <= 0:
            self.label_check_countdown.config(text="开始温度检测。")
            self.check_delay_timer_running = False
            self.switch_mode("monitor")
        else:
            self.label_check_countdown.config(text="")
            self.check_delay_timer_running = False

    def cancel_check_timer(self):
        if self.check_delay_timer_running:
            self.check_delay_timer_running = False
            self.check_delay_seconds_left = 0
            self.label_check_countdown.config(text="倒计时已取消。")

    def update_ui(self):
        try:
            # 无论在哪个界面，都更新温度信息
            if self.mode == "monitor":
                cpu_text = f"CPU温度: {self.cpu_temp:.1f} ℃" if self.cpu_temp != 0.0 else "CPU温度: 正在读取..."
                gpu_text = f"GPU温度: {self.gpu_temp:.1f} ℃" if self.gpu_temp != 0.0 else "GPU温度: 正在读取..."
                self.cpu_label.config(text=cpu_text)
                self.gpu_label.config(text=gpu_text)
            
            # 更新倒计时状态
            if self.shutdown_timer_running:
                # 在监控界面显示关机倒计时
                if self.mode == "monitor":
                    mins, secs = divmod(self.shutdown_seconds_left, 60)
                    self.label_monitor_status.config(text=f"关机倒计时：{mins}分{secs}秒")
                elif self.mode == "timer_shutdown":
                    mins, secs = divmod(self.shutdown_seconds_left, 60)
                    self.label_shutdown_countdown.config(text=f"关机倒计时：{mins}分{secs}秒")
            else:
                 if self.mode == "monitor":
                    self.label_monitor_status.config(text="") # 清除监控界面的倒计时显示
            
            if self.check_delay_timer_running and self.mode == "timer_check":
                mins, secs = divmod(self.check_delay_seconds_left, 60)
                self.label_check_countdown.config(text=f"距离温度检测开始还有 {mins}分{secs}秒")
            
            # UI每秒刷新
            self.after(1000, self.update_ui)
        except Exception as e:
            print("UI更新异常:", e)

    def stop_all_timers(self):
        # 停止所有倒计时
        self.cancel_shutdown_timer()
        self.cancel_check_timer()
        # 不再停止温度监控，让它持续运行
        # self.stop_monitoring()

    def on_close(self):
        self.stop_all_timers()
        self.monitor_thread_running = False
        self.destroy()

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print("程序异常退出:", e)
        input("按任意键退出...")

