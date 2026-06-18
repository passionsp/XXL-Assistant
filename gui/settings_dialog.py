from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QCheckBox, QSpinBox, QLabel, QTabWidget, QFormLayout, QDoubleSpinBox, QLineEdit, QDialogButtonBox, QVBoxLayout, QComboBox
from core.tasks.shiji_task import ALL_PRODUCT_NAMES  # 导入所有商品名称

class TaskSettingsDialog(QDialog):
    def __init__(self, task_name, config, parent=None):
        super().__init__(parent)
        self.task_name = task_name
        self.config = config.copy()  # 保存原始配置的副本
        self.setWindowTitle(f"{task_name} 设置")
        self.setMinimumWidth(500)  # 稍微加宽以适应商品表格
        self.product_controls = {}  # 存储 (checkbox, spinbox)
        self.action_combo = None    # 香肠伯操作下拉框
        self.init_ui()

    def init_ui(self):
        tab_widget = QTabWidget()

        # ---------- 基础设置页 ----------
        basic_widget = QWidget()
        basic_layout = QFormLayout()

        # 从桌面开始复选框
        self.launch_from_desktop = QCheckBox()
        self.launch_from_desktop.setChecked(self.config.get("launch_from_desktop", False))
        basic_layout.addRow("从桌面开始:", self.launch_from_desktop)
        basic_layout.addRow(QLabel("勾选后强制从桌面图标启动；<br>不勾选则先检测是否已在主界面，若已存在则跳过启动"))

        # 最大点击次数
        self.max_clicks = QSpinBox()
        self.max_clicks.setRange(1, 200)
        self.max_clicks.setValue(self.config.get("max_clicks", 60))
        basic_layout.addRow("最大点击中心次数:", self.max_clicks)

        # 点击间隔（秒）
        self.click_interval = QDoubleSpinBox()
        self.click_interval.setRange(0.5, 10.0)
        self.click_interval.setSingleStep(0.5)
        self.click_interval.setValue(self.config.get("click_interval", 2.0))
        basic_layout.addRow("点击间隔(秒):", self.click_interval)

        # ---------- 香肠伯任务：操作选择 ----------
        if self.task_name == "香肠伯":
            self.action_combo = QComboBox()
            self.action_combo.addItems(["领取", "掷骰"])
            self.action_combo.setCurrentText(self.config.get("action", "领取"))
            basic_layout.addRow("选择操作:", self.action_combo)

        # ---------- 市集任务：商品配置 ----------
        if self.task_name == "市集":
            products_group = QGroupBox("商品价格设置（勾选且价格≤设定值时才购买）")
            products_layout = QGridLayout()
            # 获取当前商品配置，若没有则初始化
            products_dict = self.config.get("products", {})
            # 确保所有商品都在配置中
            for name in ALL_PRODUCT_NAMES:
                if name not in products_dict:
                    products_dict[name] = {"enabled": False, "max_price": -1}
            self.config["products"] = products_dict  # 更新副本

            # 表头
            products_layout.addWidget(QLabel("购买"), 0, 0)
            products_layout.addWidget(QLabel("商品名称"), 0, 1)
            products_layout.addWidget(QLabel("最高价格"), 0, 2)

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
                self.product_controls[name] = (cb, spin)
                row += 1

            products_group.setLayout(products_layout)
            basic_layout.addRow(products_group)

        basic_widget.setLayout(basic_layout)

        # ---------- 高级设置页 ----------
        adv_widget = QWidget()
        adv_layout = QFormLayout()

        # 模板匹配阈值
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.3, 1.0)
        self.threshold.setSingleStep(0.05)
        self.threshold.setValue(self.config.get("threshold", 0.7))
        adv_layout.addRow("模板匹配阈值:", self.threshold)

        # 应用图标路径
        self.app_icon_path = QLineEdit()
        self.app_icon_path.setText(self.config.get("app_icon", "resources/imgs/app_icon.png"))
        adv_layout.addRow("应用图标模板路径:", self.app_icon_path)

        # 主界面模板路径
        self.main_template_path = QLineEdit()
        self.main_template_path.setText(self.config.get("main_template", "resources/imgs/main_screen.png"))
        adv_layout.addRow("主界面特征模板路径:", self.main_template_path)

        # 市集任务额外高级设置（最大循环次数）
        self.max_loops = QSpinBox()
        self.max_loops.setRange(5, 100)
        self.max_loops.setValue(self.config.get("max_loops", 30))
        adv_layout.addRow("最大循环次数:", self.max_loops)

        adv_widget.setLayout(adv_layout)

        tab_widget.addTab(basic_widget, "基础")
        tab_widget.addTab(adv_widget, "高级")

        # 按钮盒
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_config(self):
        """返回更新后的配置字典"""
        # 基础设置
        new_config = {
            "launch_from_desktop": self.launch_from_desktop.isChecked(),
            "max_clicks": self.max_clicks.value(),
            "click_interval": self.click_interval.value(),
            "threshold": self.threshold.value(),
            "app_icon": self.app_icon_path.text(),
            "main_template": self.main_template_path.text(),
            "max_loops": self.max_loops.value(),
        }

        # 如果是香肠伯任务，保存操作选择
        if self.task_name == "香肠伯" and self.action_combo is not None:
            new_config["action"] = self.action_combo.currentText()

        # 如果是市集任务，保存商品设置
        if self.task_name == "市集":
            products_dict = self.config.get("products", {})
            for name, (cb, spin) in self.product_controls.items():
                if name in products_dict:
                    products_dict[name]["enabled"] = cb.isChecked()
                    products_dict[name]["max_price"] = spin.value()
            new_config["products"] = products_dict

        return new_config