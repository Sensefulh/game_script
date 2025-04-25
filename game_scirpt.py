import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse, keyboard
import pyautogui
import time
import threading

class AutomationRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("自动化录制与播放工具")
        self.root.geometry("800x700")

        # 初始化变量
        self.recording = []
        self.is_recording = False
        self.is_playing = False
        self.play_thread = None

        self.screen_width, self.screen_height = pyautogui.size()  # 获取屏幕分辨率
        
        self.y_scale_factor = 0.92  # Y轴缩放因子，调整此值以缩小Y轴精度
        self.create_gui()

    def create_gui(self):
        # 状态显示
        self.status_frame = ttk.LabelFrame(self.root, text="状态", padding=10)
        self.status_frame.pack(fill='x', padx=10, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="当前状态: 空闲")
        self.status_label.pack()

        # 录制控制
        self.record_frame = ttk.LabelFrame(self.root, text="录制控制", padding=10)
        self.record_frame.pack(fill='x', padx=10, pady=5)

        self.start_button = ttk.Button(self.record_frame, text="开始录制", command=self.start_recording)
        self.start_button.pack(fill='x', pady=2)

        self.stop_button = ttk.Button(self.record_frame, text="停止录制", command=self.stop_recording, state='disabled')
        self.stop_button.pack(fill='x', pady=2)

        # 播放控制
        self.play_frame = ttk.LabelFrame(self.root, text="播放控制", padding=10)
        self.play_frame.pack(fill='x', padx=10, pady=5)

        self.loop_var = tk.BooleanVar()
        self.loop_check = ttk.Checkbutton(self.play_frame, text="循环播放", variable=self.loop_var)
        self.loop_check.pack(fill='x')

        self.repeat_frame = ttk.Frame(self.play_frame)
        self.repeat_frame.pack(fill='x')

        ttk.Label(self.repeat_frame, text="重复次数:").pack(side='left')
        self.repeat_count = ttk.Spinbox(self.repeat_frame, from_=1, to=999, width=10)
        self.repeat_count.set(1)
        self.repeat_count.pack(side='left', padx=5)

        self.play_button = ttk.Button(self.play_frame, text="开始播放", command=self.start_playback)
        self.play_button.pack(fill='x', pady=2)

        self.stop_play_button = ttk.Button(self.play_frame, text="停止播放", command=self.stop_playback, state='disabled')
        self.stop_play_button.pack(fill='x', pady=2)

        # 事件列表
        self.events_frame = ttk.LabelFrame(self.root, text="已录制事件", padding=10)
        self.events_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.events_text = tk.Text(self.events_frame, height=10)
        self.events_text.pack(fill='both', expand=True)

    def start_recording(self):
        self.is_recording = True
        self.recording = []
        self.status_label.config(text="当前状态: 录制中")
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.play_button.config(state='disabled')

        # 清空事件列表
        self.events_text.delete(1.0, tk.END)

        # 启动监听器
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        self.mouse_listener.start()

        # 延迟 10 秒再开始录制键盘
        threading.Thread(target=self.delayed_start_keyboard_listener).start()

    def delayed_start_keyboard_listener(self):
        time.sleep(10)  # 延迟 10 秒
        self.keyboard_listener.start()

    def stop_recording(self):
        self.is_recording = False
        self.status_label.config(text="当前状态: 空闲")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.play_button.config(state='normal')

        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

    def start_playback(self):
        if not self.recording:
            messagebox.showwarning("警告", "没有可播放的录制内容！")
            return

        self.is_playing = True
        self.play_button.config(state='disabled')
        self.stop_play_button.config(state='normal')
        self.start_button.config(state='disabled')

        self.play_thread = threading.Thread(target=self.playback_loop)
        self.play_thread.start()

    def stop_playback(self):
        self.is_playing = False
        self.status_label.config(text="当前状态: 空闲")
        self.play_button.config(state='normal')
        self.stop_play_button.config(state='disabled')
        self.start_button.config(state='normal')

    def playback_loop(self):
        mouse_controller = mouse.Controller()
        keyboard_controller = keyboard.Controller()

        repeat_count = int(self.repeat_count.get())

        while self.is_playing and (self.loop_var.get() or repeat_count > 0):
            self.status_label.config(text=f"当前状态: 播放中 (剩余{repeat_count}次)")

            for event in self.recording:
                if not self.is_playing:
                    break

                if event['type'] == 'mouse_click':
                    mouse_controller.position = (event['x'], event['y'])
                    if event['pressed']:
                        mouse_controller.press(event['button'])
                    else:
                        mouse_controller.release(event['button'])

                elif event['type'] == 'mouse_move':
                    mouse_controller.position = (event['x'], event['y'])

                elif event['type'] == 'key_press':
                    time.sleep(0.55)
                    keyboard_controller.press(event['key'])
                elif event['type'] == 'key_release':
                    keyboard_controller.release(event['key'])
                time.sleep(event.get('delay', 0.01))

            if not self.loop_var.get():
                repeat_count -= 1

        self.stop_playback()

    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            event = {
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': button,
                'pressed': pressed,
                'delay': 0.1
            }
            self.recording.append(event)
            self.update_events_display(f"鼠标点击: ({x}, {y})")

    def on_move(self, x, y):
        if self.is_recording:
            event = {
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'delay': 0.01
            }
            self.recording.append(event)

    def on_press(self, key):
        if self.is_recording:
            event = {
                'type': 'key_press',
                'key': key,
                'delay': 0.1
            }
            self.recording.append(event)
            self.update_events_display(f"按键按下: {key}")

    def on_release(self, key):
        if self.is_recording:
            event = {
                'type': 'key_release',
                'key': key,
                'delay': 0.1
            }
            self.recording.append(event)

    def on_scroll(self, x, y, dx, dy):
        if self.is_recording:
            event = {
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'delay': 0.01
            }
            self.recording.append(event)
            self.update_events_display(f"鼠标滚动: ({x}, {y}) 滚动量: ({dx}, {dy})")

    def update_events_display(self, text):
        self.events_text.insert(tk.END, text + '\n')
        self.events_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationRecorder(root)
    root.mainloop()
