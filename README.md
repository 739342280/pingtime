# PingTime

A simple Windows system tray application that continuously pings a user-defined address and displays real-time latency as a colored circle icon.

## Features
- 🟢🔵🟡🟠🔴⚫ Color-coded latency levels (Green → Blue → Yellow → Orange → Red → Black)
- Show exact latency in milliseconds when hovering over the tray icon
- Right-click menu to change target address (settings saved persistently)
- Lightweight, pure Python, no external dependencies except PyPI packages

## Requirements
- Python 3.6+
- Install dependencies: `pip install -r requirements.txt`

## Usage
1. Clone this repository
2. Install dependencies
3. Run `python pingtime.py`
4. The icon will appear in your system tray. Right-click → **Settings** to change the target.

## Note
The script uses `ping3` by default, which requires administrator privileges on Windows. If you prefer to run without admin, you can replace the ping logic with a system `ping` call (see comments in the code).

## License
This project is open source under the MIT License.