import json
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
from ping3 import ping

# ------------------ 配置 ------------------
CONFIG_FILE = "ping_config.json"  # 配置文件路径（与脚本同目录）

settings = {
    "target": "8.8.8.8",
    "interval": 1.5,
    "timeout": 1,
}
ICON_SIZE = 64
# ------------------------------------------

latency = None
lock = threading.Lock()

def load_settings():
    """从配置文件读取目标地址，如果文件不存在或无效则使用默认值"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "target" in data:
                    settings["target"] = data["target"]
        except (json.JSONDecodeError, KeyError, IOError):
            # 文件损坏或格式错误，忽略并使用默认值
            pass

def save_settings_to_file():
    """将当前 settings 中的关键信息写入配置文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"target": settings["target"]}, f, ensure_ascii=False, indent=2)
    except IOError:
        # 无法写入（如权限问题），静默失败，不影响运行时功能
        pass

def draw_icon(color):
    size = (ICON_SIZE, ICON_SIZE)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = 4
    draw.ellipse([margin, margin, ICON_SIZE - margin, ICON_SIZE - margin],
                 fill=color)
    return image

def get_color(ms):
    if ms is None:
        return (0, 0, 0)          # 黑色：超时/失败
    elif ms < 50:
        return (0, 255, 0)        # 绿色
    elif ms < 100:
        return (0, 128, 255)      # 蓝色
    elif ms < 150:
        return (255, 255, 0)      # 黄色
    elif ms < 200:
        return (255, 165, 0)      # 橙色
    elif ms < 500:
        return (255, 0, 0)        # 红色
    else:
        return (0, 0, 0)          # 黑色

def ping_worker(icon):
    global latency
    while True:
        target = settings["target"]
        try:
            result = ping(target, timeout=settings["timeout"], unit="ms")
            with lock:
                if result is None or result is False:
                    latency = None
                else:
                    latency = result
        except Exception:
            with lock:
                latency = None

        with lock:
            current_lat = latency
            color = get_color(current_lat)
        icon.icon = draw_icon(color)

        if current_lat is None:
            tip = f"{target} - 无响应"
        else:
            tip = f"{target} - {current_lat:.1f} ms"
        icon.title = tip

        time.sleep(settings["interval"])

def open_settings():
    """在独立线程中打开设置窗口，修改后自动保存到文件"""
    def create_window():
        root = tk.Tk()
        root.title("Ping 监视器 - 设置")
        root.geometry("300x150")
        root.resizable(False, False)

        tk.Label(root, text="目标地址 (IP/域名):").pack(pady=(15, 0))
        entry_target = tk.Entry(root, width=30)
        entry_target.insert(0, settings["target"])
        entry_target.pack(pady=5)

        def save():
            new_target = entry_target.get().strip()
            if not new_target:
                messagebox.showwarning("输入错误", "地址不能为空")
                return
            settings["target"] = new_target
            save_settings_to_file()              # 立即写入文件
            messagebox.showinfo("成功", f"已切换到: {new_target}")
            root.destroy()

        tk.Button(root, text="保存", command=save, width=12).pack(pady=10)
        root.attributes('-topmost', True)
        root.mainloop()

    threading.Thread(target=create_window, daemon=True).start()

def on_quit(icon, item):
    icon.stop()

def main():
    # 启动时加载持久化配置
    load_settings()

    initial_icon = draw_icon((128, 128, 128))
    icon = pystray.Icon(
        "ping_monitor",
        initial_icon,
        title="Ping 监视器"
    )

    menu = pystray.Menu(
        pystray.MenuItem("设置...", open_settings, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", on_quit)
    )
    icon.menu = menu

    threading.Thread(target=ping_worker, args=(icon,), daemon=True).start()
    icon.run()

if __name__ == "__main__":
    main()