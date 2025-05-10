import pyautogui
import time
clicks = 100  # 点击次数
interval = 0.5  # 点击间隔（秒）

# 等待几秒钟切换到目标窗口
print("请在 5 秒内切换到目标窗口...")
time.sleep(5)
# 开始连点
for i in range(clicks):
    pyautogui.click()
    time.sleep(interval)

print("连点完成！")
