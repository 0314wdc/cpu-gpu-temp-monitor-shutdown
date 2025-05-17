# cpu-gpu-temp-monitor-shutdown
# 温度监控与定时控制

##描述
## 项目描述

This is a simple Python application built with Tkinter and OpenHardwareMonitorLib that monitors CPU and GPU temperatures. It provides options for automatic system shutdown based on temperature thresholds after a delay, as well as manual timed shutdown and timed temperature checks.

这是一个使用Tkinter和OpenHardwareMonitorLib构建的简单Python应用程序，用于监控CPU和GPU温度。它提供了基于温度阈值延迟自动关机的功能，以及手动定时关机和定时温度检测的功能。

## Features
## 主要功能

- Real-time CPU and GPU temperature monitoring.
- Automatic system shutdown when both CPU and GPU temperatures drop below configurable thresholds for a specified delay.
- Manual timed system shutdown.
- Manual timed delay before starting temperature monitoring.
- Configuration saved to a `config.json` file.
- Runs with administrator privileges (required for hardware monitoring and shutdown).

- 实时监控CPU和GPU温度。
- 当CPU和GPU温度在指定延迟后同时低于可配置的阈值时，自动关机。
- 手动设置定时关机。
- 手动设置延迟一段时间后开始温度检测。
- 配置保存在 `config.json` 文件中。
- 需要管理员权限运行（用于硬件监控和关机）。

## Target Audience
## 目标用户

This tool is designed for users, such as gamers, who want to automatically shut down their computer after high-load tasks (like gaming) when the system has cooled down to a safe temperature, or who need simple timed shutdown/check functionalities.

此工具专为希望在完成高负载任务（如游戏）后，当系统温度降至安全水平时自动关机，或需要简单定时关机/检测功能的用户（例如游戏玩家）设计。

## Included Files (in `dist` folder)
## 包含的文件（在 `dist` 文件夹中）

When you download the contents of the `dist` folder, you will find the following files:

下载 `dist` 文件夹的内容后，您将看到以下文件：

- `temp_monitor.exe`: The executable file. This is a standalone application that can be run directly without installing Python or dependencies.
- `OpenHardwareMonitorLib.dll`: The necessary library for hardware monitoring. It is included with the executable.
- `config.json`: The configuration file. If this file does not exist when the application starts, it will be automatically generated with default settings.
- `temp_monitor.py`: The source code of the application.

- `temp_monitor.exe`: 可执行文件。这是一个独立应用程序，无需安装Python或依赖即可直接运行。
- `OpenHardwareMonitorLib.dll`: 硬件监控所需的库文件，已包含在可执行文件中。
- `config.json`: 配置文件。如果应用程序启动时此文件不存在，将自动生成默认配置。
- `temp_monitor.py`: 应用程序的源代码。

## Usage
## 使用方法

1. Download the contents of the `dist` folder.
2. Run `temp_monitor.exe`.
3. The application requires administrator privileges to run. If not run as administrator, it will attempt to restart itself with elevated privileges.
4. The `config.json` file will be automatically created in the same directory as the executable if it doesn't exist. You can edit this file or use the application's UI to change temperature thresholds, shutdown delay, check interval, and timer settings.
5. Use the navigation tabs ("温度监控", "定时关机", "定时检测") to switch between different functionalities.

1. 下载 `dist` 文件夹中的内容。
2. 运行 `temp_monitor.exe`。
3. 应用程序需要管理员权限才能运行。如果不是以管理员身份运行，它将尝试以提升的权限重新启动。
4. 如果 `config.json` 文件不存在，它将在可执行文件所在的同一目录下自动创建。您可以编辑此文件或使用应用程序的用户界面来更改温度阈值、关机延迟、检测间隔和定时设置。
5. 使用导航栏选项卡（“温度监控”、“定时关机”、“定时检测”）切换不同功能。

## Building from Source
## 从源代码构建

If you wish to build the executable from the source code (`temp_monitor.py`), you will need Python and PyInstaller. Ensure you have the `OpenHardwareMonitorLib.dll` file in the same directory as the script or update the `dll_path` in the script.

如果您希望从源代码（`temp_monitor.py`）构建可执行文件，您需要安装Python和PyInstaller。请确保 `OpenHardwareMonitorLib.dll` 文件与脚本在同一目录下，或更新脚本中的 `dll_path`。

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "OpenHardwareMonitorLib.dll;." temp_monitor.py
```

This will generate the `dist` folder containing the executable and the DLL.
