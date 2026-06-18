import sys
import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTime
from core.controller import GameController
from core.tasks.login_task import LoginTask
from core.tasks.guild_reward_task import GuildRewardTask
from core.tasks.peiyu_task import PeiyuTask
from core.tasks.shiji_task import ShijiTask
from core.tasks.shiji_task import ALL_PRODUCT_NAMES
from core.tasks.dailytask_task import DailytaskTask
from core.tasks.sausage_task import SausageTask
from core.tasks.invite_task import InviteTask
CONFIG_FILE = "config/tasks_config.json"

class TaskThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.task.log_signal.connect(self.log_signal.emit)
        self.task.finished_signal.connect(self.finished_signal.emit)

    def run(self):
        self.task.run()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XXL 助手")
        self.setGeometry(100, 100, 1100, 700)

        # 初始化核心控制器
        try:
            self.controller = GameController()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设备连接失败: {e}")
            sys.exit(1)

        # 任务注册表（默认配置）
        self.tasks = {
            "登录游戏": {
                "class": LoginTask,
                "config": {
                    "launch_from_desktop": False,
                    "app_icon": "imgs/app_icon.png",
                    "main_template": "imgs/main_screen.png",
                    "max_clicks": 60,
                    "click_interval": 2.0,
                    "threshold": 0.7
                }
            },
            "公会奖励": {
                "class": GuildRewardTask,
                "config": {
                    "threshold": 0.7,
                    "guild_btn": "imgs/guild_btn.png",
                    "guild_task_btn": "imgs/guild_task_btn.png",
                    "yijianlingqu": "imgs/yijianlingqu.png",
                    "back_btn": "imgs/back_btn.png",
                    "wishing_well_btn": "imgs/wishing_well_btn.png",
                    "donate_btn": "imgs/donate_btn.png",
                    "confirm_donate_btn": "imgs/confirm_donate_btn.png",
                    "main_template": "imgs/main_screen.png",
                    # 蓝星区域: 左上角(250, 250), 右下角(280, 280) => 宽30, 高30
                    "blue_star_region": [250, 250, 30, 30],
                    "purple_star_region": [460, 250, 30, 30],
                    "yellow_star_region": [670, 250, 30, 30],
                    "max_donate_loops": 10
            }
                },
            "培育": {
                "class": PeiyuTask,
                "config": {
                    "threshold": 0.7,
                    "peiyu_btn": "imgs/peiyu_btn.png",
                    "qihedu_btn": "imgs/qihedu_btn.png",
                    "jinqu_btn": "imgs/jinqu_btn.png",
                    "choupai_btn": "imgs/choupai_btn.png",
                    "queding_btn": "imgs/queding_btn.png",
                    "back_btn": "imgs/back_btn.png",
                    "main_template": "imgs/main_screen.png",
                    "item_count_region": [800, 120, 20, 20],
                    "piaojuan_ocr_region": [580,840,30,20]
                    # 根据实际位置调整
                }
            },
            "市集": {
                "class": ShijiTask,
                "config": {
                    "threshold": 0.7,
                    "shiji_btn": "imgs/shiji_btn.png",
                    "goumai_btn": "imgs/goumai_btn.png",
                    "shuaxin_btn": "imgs/shuaxin_btn.png",
                    "piaojuan_shuaxin_btn": "imgs/piaojuan_shuaxin_btn.png",
                    "quxiao_btn": "imgs/quxiao_btn.png",
                    "back_btn": "imgs/back_btn.png",
                    "main_template": "imgs/main_screen.png",
                    "products": {
                        "速通票": {"enabled": True, "max_price": 10},
                        "征才广告": {"enabled": True, "max_price": 10},
                        "健身中心入场券": {"enabled": False, "max_price": 0},
                        "困难模式入场券": {"enabled": False, "max_price": 0},
                        "能量大满罐": {"enabled": True, "max_price": 15},
                        "金酒铃": {"enabled": True, "max_price": 30},
                        "观光工坊入场券": {"enabled": False, "max_price": 0},
                        "特卖型录": {"enabled": True, "max_price": 10},
                        "能量饮料": {"enabled": True, "max_price": 8},
                        "培欲房卡": {"enabled": False, "max_price": 0},
                        "入门营养惊喜包": {"enabled": False, "max_price": 0},
                        "进阶营养惊喜包": {"enabled": False, "max_price": 0},
                        "中级营养惊喜包": {"enabled": False, "max_price": 0},
                        "心得兑换券": {"enabled": False, "max_price": 0},
                        "空白碎片惊喜包": {"enabled": False, "max_price": 0},
                        "精华": {"enabled": False, "max_price": 0}
                    },
                    "max_loops": 30
                }
            },
            "每日任务": {
                    "class": DailytaskTask,
                    "config": {
                        "threshold": 0.7,
                        "task_btn": "imgs/task_btn.png",
                        "yijianlingqu_btn": "imgs/yijianlingqu_btn.png",
                        "back_btn": "imgs/back_btn.png",
                        "main_template": "imgs/main_screen.png",
                    }
                },
            "香肠伯": {
                    "class": SausageTask,
                    "config": {
                        "threshold": 0.7,
                        "sausage_btn": "imgs/sausage_btn.png",
                        "direct_claim_btn": "imgs/direct_claim_btn.png",
                        "roll_btn": "imgs/roll_btn.png",
                        "back_btn": "imgs/back_btn.png",
                        "main_template": "imgs/main_screen.png",
                        "action": "领取"  # 可选值："领取" 或 "掷骰"
                    }
                },
            "召唤": {
                    "class": InviteTask,
                    "config": {
                        "threshold": 0.7,
                        "invite_btn": "imgs/invite_btn.png",
                        "single_summon_btn": "imgs/single_summon_btn.png",
                        "back_btn": "imgs/back_btn.png",
                        "main_template": "imgs/main_screen.png",
                        "quxiao_summon_btn": "imgs/quxiaozhaohuan_btn.png"
                    }
                }
        }

        self.load_task_configs()
        self.init_ui()
        self.current_thread = None

    def init_ui(self):
        # 主分割器：左、中、右
        main_splitter = QSplitter(Qt.Horizontal)

        # ========== 左侧：任务列表（带齿轮按钮） ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        self.task_list = QListWidget()
        # 为每个任务添加自定义项（包含任务名和齿轮按钮）
        for task_name in self.tasks.keys():
            self.add_task_item(task_name)

        left_layout.addWidget(QLabel("可选任务"))
        left_layout.addWidget(self.task_list)

        self.start_btn = QPushButton("开始执行")
        self.start_btn.clicked.connect(self.start_task)
        left_layout.addWidget(self.start_btn)

        left_widget.setLayout(left_layout)

        # ========== 中间：设置面板容器（默认显示空面板） ==========
        self.middle_stack = QStackedWidget()
        self.empty_widget = QLabel("点击任务旁的齿轮按钮以设置任务参数")
        self.empty_widget.setAlignment(Qt.AlignCenter)
        self.empty_widget.setStyleSheet("color: gray; font-size: 14px;")
        self.middle_stack.addWidget(self.empty_widget)  # index 0
        self.settings_widgets = {}  # task_name -> 面板widget

        # ========== 右侧：日志区 ==========
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(QLabel("执行日志"))
        right_layout.addWidget(self.log_text)
        right_widget.setLayout(right_layout)

        # 将三个部件加入分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(self.middle_stack)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([200, 400, 300])

        self.setCentralWidget(main_splitter)

    def add_task_item(self, task_name):
        """为任务列表添加一个带复选框和齿轮按钮的项"""
        item = QListWidgetItem(self.task_list)
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        # 复选框
        cb = QCheckBox()
        cb.setChecked(True)  # 默认勾选
        layout.addWidget(cb)

        label = QLabel(task_name)
        btn = QPushButton("⚙️")
        btn.setFixedSize(30, 30)
        btn.setToolTip(f"设置 {task_name}")
        btn.clicked.connect(lambda checked, name=task_name: self.show_task_settings(name))

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.task_list.setItemWidget(item, widget)
    
    # 保存复选框引用（可选，用于获取勾选状态）
    # 我们可以通过 itemWidget 获取，所以不需要额外存储
    def get_checked_tasks(self):
        """按列表顺序返回所有勾选的任务名称列表"""
        checked = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget:
                # 找到复选框
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked():
                    # 找到标签获取任务名
                    label = widget.findChild(QLabel)
                    if label:
                        checked.append(label.text())
        return checked
    def show_task_settings(self, task_name):
        """点击齿轮时，创建或切换到该任务的设置面板"""
        # 如果已经存在该任务的面板，直接切换
        if task_name in self.settings_widgets:
            panel = self.settings_widgets[task_name]
            self.middle_stack.setCurrentWidget(panel)
            return

        # 创建新的设置面板
        config = self.tasks[task_name]["config"].copy()
        panel = self.create_settings_panel(task_name, config)
        self.settings_widgets[task_name] = panel
        self.middle_stack.addWidget(panel)
        self.middle_stack.setCurrentWidget(panel)

    def create_settings_panel(self, task_name, config):
        """创建带基础/高级选项卡的设置面板，并实时保存配置"""
        from PyQt5.QtWidgets import QTabWidget, QWidget, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit, QGroupBox, QGridLayout, QLabel

        tab_widget = QTabWidget()

        # ----- 基础设置页 -----
        basic_widget = QWidget()
        basic_layout = QFormLayout()

        cb_launch = QCheckBox()
        cb_launch.setChecked(config.get("launch_from_desktop", False))
        basic_layout.addRow("从桌面开始:", cb_launch)

        spin_max = QSpinBox()
        spin_max.setRange(1, 200)
        spin_max.setValue(config.get("max_clicks", 60))
        basic_layout.addRow("最大点击中心次数:", spin_max)

        double_interval = QDoubleSpinBox()
        double_interval.setRange(0.5, 10.0)
        double_interval.setSingleStep(0.5)
        double_interval.setValue(config.get("click_interval", 2.0))
        basic_layout.addRow("点击间隔(秒):", double_interval)
        # 如果是香肠伯任务，添加操作选择
        if task_name == "香肠伯":
            action_combo = QComboBox()
            action_combo.addItems(["领取", "掷骰"])
            action_combo.setCurrentText(config.get("action", "领取"))
            basic_layout.addRow("选择操作:", action_combo)
        else:
            action_combo = None
        # ========== 如果是市集任务，添加商品配置 ==========
        if task_name == "市集":
            # 获取当前商品配置，若没有则初始化
            products_dict = config.get("products", {})
            for name in ALL_PRODUCT_NAMES:
                if name not in products_dict:
                    products_dict[name] = {"enabled": False, "max_price": -1}
            config["products"] = products_dict  # 更新本地副本

            products_group = QGroupBox("商品价格设置（勾选且价格≤设定值时才购买）")
            products_layout = QGridLayout()
            products_layout.addWidget(QLabel("购买"), 0, 0)
            products_layout.addWidget(QLabel("商品名称"), 0, 1)
            products_layout.addWidget(QLabel("最高价格"), 0, 2)

            product_widgets = {}  # 存储控件: {name: (cb, spin)}
            row = 1
            for name in ALL_PRODUCT_NAMES:
                cfg = products_dict.get(name, {"enabled": False, "max_price": -1})
                cb = QCheckBox()
                cb.setChecked(cfg.get("enabled", False))
                label = QLabel(name)
                spin = QSpinBox()
                spin.setRange(-1, 9999)
                spin.setValue(cfg.get("max_price", -1))
                spin.setToolTip("设为-1表示永不购买")
                products_layout.addWidget(cb, row, 0)
                products_layout.addWidget(label, row, 1)
                products_layout.addWidget(spin, row, 2)
                product_widgets[name] = (cb, spin)
                row += 1

            products_group.setLayout(products_layout)
            basic_layout.addRow(products_group)
        else:
            product_widgets = {}  # 非市集任务不涉及

        basic_widget.setLayout(basic_layout)

        # ----- 高级设置页 -----
        adv_widget = QWidget()
        adv_layout = QFormLayout()

        double_thresh = QDoubleSpinBox()
        double_thresh.setRange(0.3, 1.0)
        double_thresh.setSingleStep(0.05)
        double_thresh.setValue(config.get("threshold", 0.7))
        adv_layout.addRow("模板匹配阈值:", double_thresh)

        le_icon = QLineEdit()
        le_icon.setText(config.get("app_icon", "imgs/app_icon.png"))
        adv_layout.addRow("应用图标模板:", le_icon)

        le_main = QLineEdit()
        le_main.setText(config.get("main_template", "imgs/main_screen.png"))
        adv_layout.addRow("主界面模板:", le_main)

        # 市集任务额外高级设置（最大循环次数）
        if task_name == "市集":
            spin_loops = QSpinBox()
            spin_loops.setRange(5, 100)
            spin_loops.setValue(config.get("max_loops", 30))
            adv_layout.addRow("最大循环次数:", spin_loops)
        else:
            spin_loops = None

        adv_widget.setLayout(adv_layout)

        tab_widget.addTab(basic_widget, "基础")
        tab_widget.addTab(adv_widget, "高级")

        # 保存控件引用，以便实时更新配置
        panel_data = {
            "task_name": task_name,
            "widgets": {
                "launch_from_desktop": cb_launch,
                "max_clicks": spin_max,
                "click_interval": double_interval,
                "threshold": double_thresh,
                "app_icon": le_icon,
                "main_template": le_main,
            },
            "product_widgets": product_widgets if task_name == "市集" else {},
            "max_loops": spin_loops if task_name == "市集" else None,
            "action_combo": action_combo if task_name == "香肠伯" else None,
        }
        tab_widget.setProperty("panel_data", panel_data)

        # 连接信号，实时更新 self.tasks 并保存
        for w in panel_data["widgets"].values():
            if action_combo:
                action_combo.currentTextChanged.connect(lambda: self.update_task_config_from_panel(task_name))
            if hasattr(w, 'valueChanged'):
                w.valueChanged.connect(lambda: self.update_task_config_from_panel(task_name))
            elif hasattr(w, 'textChanged'):
                w.textChanged.connect(lambda: self.update_task_config_from_panel(task_name))
            elif hasattr(w, 'toggled'):
                w.toggled.connect(lambda: self.update_task_config_from_panel(task_name))
            
        # 连接商品控件信号（如果有）
        for name, (cb, spin) in panel_data["product_widgets"].items():
            cb.toggled.connect(lambda: self.update_task_config_from_panel(task_name))
            spin.valueChanged.connect(lambda: self.update_task_config_from_panel(task_name))
        
        if panel_data["max_loops"]:
            panel_data["max_loops"].valueChanged.connect(lambda: self.update_task_config_from_panel(task_name))

        return tab_widget
    def update_task_config_from_panel(self, task_name):
        """从设置面板读取当前值，更新到 self.tasks[task_name]['config'] 并保存"""
        panel = self.settings_widgets.get(task_name)
        if not panel:
            return
        data = panel.property("panel_data")
        if not data:
            return

        widgets = data["widgets"]
        new_config = {
            "launch_from_desktop": widgets["launch_from_desktop"].isChecked(),
            "max_clicks": widgets["max_clicks"].value(),
            "click_interval": widgets["click_interval"].value(),
            "threshold": widgets["threshold"].value(),
            "app_icon": widgets["app_icon"].text(),
            "main_template": widgets["main_template"].text(),
        }

        # 如果是市集任务，保存商品设置和最大循环次数
        if task_name == "市集":
            product_widgets = data.get("product_widgets", {})
            if product_widgets:
                products_dict = self.tasks[task_name]["config"].get("products", {})
                for name, (cb, spin) in product_widgets.items():
                    if name in products_dict:
                        products_dict[name]["enabled"] = cb.isChecked()
                        products_dict[name]["max_price"] = spin.value()
                new_config["products"] = products_dict
            if data.get("max_loops"):
                new_config["max_loops"] = data["max_loops"].value()

        # 更新并保存
        self.tasks[task_name]["config"].update(new_config)
        self.save_task_configs()
    def start_task(self):
        # 获取所有勾选的任务
        task_names = self.get_checked_tasks()
        if not task_names:
            self.log("请至少勾选一个任务")
            return
        
        self.log(f"准备执行 {len(task_names)} 个任务: {', '.join(task_names)}")
        self.task_queue = task_names
        self.current_task_index = 0
        self.start_btn.setEnabled(False)
        self.start_btn.setText("执行中...")
        # 禁用列表，防止执行期间修改勾选状态
        self.task_list.setEnabled(False)
        self.execute_next_task()

    def log(self, msg):
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        self.log_text.append(f"[{timestamp}] {msg}")

    # 配置持久化
    def load_task_configs(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    for task_name, config in saved.items():
                        if task_name in self.tasks:
                            self.tasks[task_name]["config"].update(config)
            except Exception as e:
                print(f"加载配置失败: {e}")

    def save_task_configs(self):
        data = {}
        for task_name, info in self.tasks.items():
            data[task_name] = info["config"]
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    def execute_next_task(self):
        if self.current_task_index >= len(self.task_queue):
            # 所有任务执行完毕
            self.start_btn.setEnabled(True)
            self.start_btn.setText("开始执行")
            self.task_list.setEnabled(True)
            self.log("所有任务执行完毕")
            self.task_queue = []
            return
        
        task_name = self.task_queue[self.current_task_index]
        self.log(f"开始执行任务 ({self.current_task_index+1}/{len(self.task_queue)}): {task_name}")
        
        # 确保配置是最新的（如果设置面板打开过，已经自动保存；未打开则使用默认配置）
        self.update_task_config_from_panel(task_name)  # 保留原有的配置更新逻辑
        
        task_class = self.tasks[task_name]["class"]
        task_config = self.tasks[task_name]["config"]
        
        task = task_class(self.controller, task_config)
        self.current_thread = TaskThread(task)
        self.current_thread.log_signal.connect(self.log)
        # 注意：finished_signal 连接到 on_task_finished，用于触发下一个任务
        self.current_thread.finished_signal.connect(self.on_task_finished)
        self.current_thread.start()
    def on_task_finished(self, success):
        task_name = self.task_queue[self.current_task_index]
        self.log(f"任务 '{task_name}' {'成功' if success else '失败'}")
        self.current_task_index += 1
        # 这里可以根据需求决定失败时是否继续，当前实现：失败则停止后续任务
        if not success:
            self.log("任务失败，停止执行后续任务")
            self.start_btn.setEnabled(True)
            self.start_btn.setText("开始执行")
            self.task_list.setEnabled(True)
            self.task_queue = []
            return
        # 继续执行下一个任务
        self.execute_next_task()