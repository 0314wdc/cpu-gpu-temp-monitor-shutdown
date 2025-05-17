# cpu-gpu-temp-monitor-shutdown
# CPU/GPU温度监控与自动关机系统

##描述
## 项目描述

This is a simple Python application built with Tkinter and OpenHardwareMonitorLib that monitors CPU and GPU temperatures. It provides options for automatic system shutdown based on temperature thresholds after a delay, as well as manual timed shutdown and timed temperature checks.

这是一个使用Tkinter和OpenHardwareMonitorLib构建的简单Python应用程序，用于监控CPU和GPU温度。它提供了根据配置延迟自动关机的功能，以及手动定时关机和定时温度检测的功能。

## Features
## 主要功能

- Real-time CPU and GPU temperature monitoring.
- Automatic system shutdown when both CPU and GPU temperatures drop below configurable thresholds for a specified delay.
- Manual timed system shutdown.
- Manual timed delay before starting temperature monitoring.
- Configuration saved to a `config.json` file.
- Runs with administrator privileges (required for hardware monitoring and shutdown).
- Currently supports Windows only, updates needed for other systems.

- 实时监控CPU和GPU温度。
- 当CPU和GPU温度在指定延迟后同时低于可配置的阈值时，根据配置延迟自动关机。
- 手动设置定时关机。
- 手动设置延迟一段时间后开始温度检测。
- 配置保存在 `config.json` 文件中。
- 需要管理员权限运行（用于硬件监控和关机）。
- 目前仅支持Windows，需要更新请支持。

## Target Audience
## 目标用户

This tool is designed for users, such as gamers, who want to automatically shut down their computer after high-load tasks (like gaming) when the system has cooled down to a safe temperature, or who need simple timed shutdown/check functionalities.

此工具专为希望在完成高负载任务（如游戏）后，当系统温度降至安全水平时自动关机，或需要简单定时关机/检测功能的用户（例如游戏玩家）设计。

## Usage
## 使用方法

1. Run `temp_monitor.exe`.
2. The application requires administrator privileges to run. If not run as administrator, it will attempt to restart itself with elevated privileges.
3. The `config.json` file will be automatically created in the same directory as the executable if it doesn't exist. You can edit this file or use the application's UI to change temperature thresholds, shutdown delay, check interval, and timer settings.
4. Use the navigation tabs ("温度监控", "定时关机", "定时检测") to switch between different functionalities.

1. 运行 `temp_monitor.exe`。
2. 应用程序需要管理员权限才能运行。如果不是以管理员身份运行，它将尝试以提升的权限重新启动。
3. 如果 `config.json` 文件不存在，它将在可执行文件所在的同一目录下自动创建。您可以编辑此文件或使用应用程序的用户界面来更改温度阈值、关机延迟、检测间隔和定时设置。
4. 使用导航栏选项卡（“温度监控”、“定时关机”、“定时检测”）切换不同功能。

## Building from Source
## 从源代码构建

If you wish to build the executable from the source code (`temp_monitor.py`), you will need Python and PyInstaller. Ensure you have the `OpenHardwareMonitorLib.dll` file in the same directory as the script or update the `dll_path` in the script.

如果您希望从源代码（`temp_monitor.py`）构建可执行文件，您需要安装Python和PyInstaller。请确保 `OpenHardwareMonitorLib.dll` 文件与脚本在同一目录下，或更新脚本中的 `dll_path`。

如你还未安装 pythonnet，可以打开命令行输入：

```bash
pip install pythonnet
```
