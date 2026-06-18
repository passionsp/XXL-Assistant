import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template

class LoginTask(BaseTask):
    def run(self):
        self.log_signal.emit("开始执行登录任务...")

        launch_from_desktop = self.config.get("launch_from_desktop", False)
        app_icon_path = self.config.get("app_icon", "resources/imgs/app_icon.png")
        main_template_path = self.config.get("main_template", "resources/imgs/main_screen.png")
        max_clicks = self.config.get("max_clicks", 60)
        click_interval = self.config.get("click_interval", 2.0)
        threshold = self.config.get("threshold", 0.7)

        # 先检测当前是否已经在主界面（若不要求从桌面开始）
        if not launch_from_desktop:
            self.log_signal.emit("检查是否已在主界面...")
            img = self.controller.screenshot()
            if find_template(img, main_template_path, threshold=threshold):
                self.log_signal.emit("检测到已在主界面，跳过启动流程。")
                self.finished_signal.emit(True)
                return
            else:
                self.log_signal.emit("未在主界面，执行完整启动流程。")
        else:
            self.log_signal.emit("【从桌面开始】模式，将强制从桌面图标启动。")

        # ----- 以下为完整启动流程（从桌面图标开始）-----
        # 1. 等待并点击应用图标
        self.log_signal.emit("等待应用图标...")
        icon_found = False
        for _ in range(10):   # 最多尝试10秒
            img = self.controller.screenshot()
            pos = find_template(img, app_icon_path, threshold=threshold)
            if pos:
                self.controller.tap(*pos)
                icon_found = True
                break
            time.sleep(1)
        if not icon_found:
            self.log_signal.emit("未找到应用图标，启动失败。")
            self.finished_signal.emit(False)
            return

        self.log_signal.emit("已点击图标，等待游戏启动...")
        time.sleep(5)   # 等待横竖屏切换

        # 2. 循环点击屏幕中心，直到主界面出现
        for attempt in range(max_clicks):
            img = self.controller.screenshot()
            w, h = img.size
            if find_template(img, main_template_path, threshold=threshold):
                self.log_signal.emit("检测到主界面！登录成功")
                self.finished_signal.emit(True)
                return
            # 点击屏幕中心
            self.controller.tap(w//2, h//2)
            self.log_signal.emit(f"第{attempt+1}次点击中心，等待加载...")
            time.sleep(click_interval)

        self.log_signal.emit("登录超时，未能进入主界面")
        self.finished_signal.emit(False)