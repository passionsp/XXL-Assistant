
---

# XXL Assistant

> 一款基于计算机视觉的移动游戏自动化助手，帮助玩家自动完成日常任务。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 📖 简介

XXL Assistant 是一款针对手游日常任务开发的自动化工具，通过图像识别（OpenCV + ddddocr）和 ADB 设备控制，模拟真实用户操作，自动完成游戏内的重复性任务。项目采用 **核心引擎与 GUI 分离** 的模块化架构，支持多任务队列执行、可视化参数配置和实时日志输出。

目前已实现的功能模块：
- ✅ 登录游戏（支持从桌面启动或快速检测已进入主界面）
- ✅ 公会奖励（含滑块拖拽与 OCR 数值识别）
- ✅ 培育
- ✅ 市集（OCR 识别 15 个商品名称和价格，支持价格阈值购买）
- ✅ 每日任务
- ✅ 香肠伯（用户可配置“领取”或“掷骰”）
- ✅ 召唤（含取消判断）
- 更多模块持续开发中...

---

## 📦 下载与运行

本项目为开源 Python 项目，推荐直接运行源码。

### 1. 克隆仓库
```bash
git clone https://github.com/passionsp/XXL-Assistant.git
cd XXL-Assistant
```

### 2. 创建并激活虚拟环境（推荐）
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行程序
```bash
python main.py
```

---

## 🚀 使用前准备

### 1. 安装 ADB 并配置环境变量
- 下载 [Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- 将 `adb.exe` 所在目录添加到系统 PATH 中
- 在命令行输入 `adb version` 验证是否成功

### 2. 启动安卓模拟器或连接真机
- 推荐使用 **雷电模拟器**，并开启 ADB 调试
- 确保模拟器与电脑连接正常（`adb devices` 可看到设备）

### 3. 准备模板图片
- 项目需要 `imgs/` 目录下的模板图片（用于按钮识别）
- 如果您的游戏分辨率不是 900×1600，需要重新截图裁剪模板
- 初始模板可在仓库的 `imgs/` 目录中找到，或根据实际界面自行截图替换

### 4. 配置任务参数
- 启动程序后，点击任务右侧的齿轮按钮，可分别配置每个任务的详细参数
- 市集任务需要手动勾选商品并设置最高购买价格
- 配置会自动保存到 `config/tasks_config.json`

---

## 📝 使用方法

1. **启动程序**：运行 `python main.py`
2. **勾选任务**：在任务列表中勾选你想要执行的任务（支持多选）
3. **设置参数**：点击任务旁的齿轮图标，根据需求调整参数
4. **开始执行**：点击左下角的“开始执行”按钮，程序将按顺序运行所有勾选的任务
5. **查看日志**：右侧日志区域会实时输出任务执行进度和识别结果

---

## 🛠 开发与扩展

### 添加新任务
1. 在 `core/tasks/` 下新建任务类，继承 `BaseTask`
2. 实现 `run` 方法，在方法内部使用 `self.log_signal.emit()` 输出日志，使用 `self.finished_signal.emit(True/False)` 标记任务完成状态
3. 在 `main_window.py` 的 `self.tasks` 字典中注册任务，配置默认参数
4. 如需在设置面板中增加自定义控件，修改 `create_settings_panel` 方法

### 调整图像识别参数
- 模板匹配阈值可在任务配置中调整 `"threshold"`
- OCR 识别区域坐标可在 `shiji_task.py` 的 `product_regions` 中修改
- 字符替换规则在 `ocr_region` 方法中定义

---

## ❓ 常见问题

**Q: 提示找不到 ADB 设备？**  
A: 确保模拟器已开启 ADB 调试，并在命令行执行 `adb devices` 查看设备列表。如果仍未显示，尝试重启模拟器或重新连接。

**Q: 市集商品识别失败怎么办？**  
A: 市集使用 ddddocr 识别商品名称和价格，如果识别不准确，可以在 `shiji_task.py` 中调整 OCR 区域坐标或二值化阈值。你也可以在日志中查看原始 OCR 结果，据此优化 `PRODUCT_MAPPING` 的关键词列表。

**Q: 滑块拖拽无效？**  
A: 确保配置中的滑块起始和终点坐标正确（基于 900×1600 分辨率）。如分辨率不同，可在代码中缩放坐标。

**Q: 程序运行报错 `ModuleNotFoundError`？**  
A: 请确保所有依赖已正确安装，可以尝试 `pip install -r requirements.txt` 重新安装。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！如果你有新的任务模块想要添加，可以继承 `BaseTask` 并实现 `run` 方法，然后在 `main_window.py` 中注册即可。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)，可自由使用、修改和分发。

---

## 🙏 致谢

- 参考了 [MAA (MaaAssistantArknights)](https://github.com/MaaAssistantArknights) 的分离式设计理念
- 使用 [ddddocr](https://github.com/sml2h3/ddddocr) 进行轻量级 OCR 识别
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) 提供界面支持

---

**Enjoy!** 🎮☕