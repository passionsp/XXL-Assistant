from PyQt5.QtCore import QObject, pyqtSignal
from core.recognizer import find_template
import time
class BaseTask(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(int)  # 可选

    def __init__(self, controller, config=None):
        super().__init__()
        self.controller = controller
        self.config = config or {}

    def run(self):
        """子类必须实现，内部发射信号"""
        raise NotImplementedError
    def ensure_main_screen(self, max_attempts=20, interval=2.0):
        """
        确保当前在主界面。如果不在，则循环点击返回按钮直到回到主界面。
        需要配置中有 main_template 和 threshold。
        """
        main_template = self.config.get("main_template")
        if not main_template:
            self.log_signal.emit("警告：未配置 main_template，无法检测主界面，跳过检查")
            return True

        threshold = self.config.get("threshold", 0.7)
        from core.recognizer import find_template

        for attempt in range(max_attempts):
            img = self.controller.screenshot()
            if find_template(img, main_template, threshold=threshold):
                self.log_signal.emit("已在主界面")
                return True
            self.log_signal.emit(f"未在主界面，尝试返回 (第 {attempt+1} 次)")
            back_btn = self.config.get("back_btn", "imgs/back_btn.png")
            # 直接点击返回按钮，不依赖 click_btn（避免递归）
            # 但我们可以使用 click_btn，但需要传入 threshold 和 required=False
            if hasattr(self, 'click_btn'):
                self.click_btn(back_btn, threshold, required=False, timeout=2)
            else:
                # 如果基类没有 click_btn，则使用 controller.tap 但需找按钮位置
                # 这里因为子类都有 click_btn，所以不会走这个分支
                pos = find_template(img, back_btn, threshold=threshold)
                if pos:
                    self.controller.tap(pos[0], pos[1])
            time.sleep(interval)

        self.log_signal.emit("无法回到主界面，检查超时")
        return False
    def click_btn(self, template_path, threshold, required=True, timeout=5):
        start = time.time()
        while time.time() - start < timeout:
            img = self.controller.screenshot()
            pos = find_template(img, template_path, threshold=threshold)
            if pos:
                self.controller.tap(pos[0], pos[1])
                return True
            time.sleep(0.5)
        if required:
            self.log_signal.emit(f"找不到按钮: {template_path}")
        return False