import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template
class DagongTask(BaseTask):
    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行每日任务...")
        threshold = self.config.get("threshold", 0.7)
        # 加载按钮模板
        dagong_btn = self.config.get("dagong_btn", "imgs/dagong_btn.png")
        yijiandagong_btn = self.config.get("yijiandagong_btn", "imgs/yijiandagong_btn.png")
        yijianlingqu_btn = self.config.get("yijianlingqu_btn", "imgs/yijianlingqu.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")
        quedingdagong_btn = self.config.get("quedingdagong_btn", "imgs/quedingdagong_btn.png")
        if not self.click_btn(dagong_btn, threshold):
            self.log_signal.emit("未找到打工按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(2)
        if not self.click_btn(yijiandagong_btn, threshold):
            if not self.click_btn(yijianlingqu_btn, threshold):
                self.log_signal.emit("未找到一键打工或一键领取按钮，任务终止")
                self.click_btn(back_btn, threshold)  # 尝试返回主界面
                self.log_signal.emit("尝试返回主界面")
                self.finished_signal.emit(False)
                return
            else:
                time.sleep(2)
                img = self.controller.screenshot()
                w, h = img.size
                self.controller.tap(w//2, h//2)
                self.log_signal.emit("点击屏幕中心（任意处）")
                time.sleep(1)

        else:
            if not self.click_btn(quedingdagong_btn, threshold):
                self.log_signal.emit("未找到开始打工按钮，任务终止")
                self.click_btn(back_btn, threshold)  # 尝试返回主界面
                self.log_signal.emit("尝试返回主界面")
                self.finished_signal.emit(False)
                img = self.controller.screenshot()
                if find_template(img, main_template, threshold=threshold):
                    self.log_signal.emit("已回到主界面，打工任务未完成")
                else:
                    self.log_signal.emit("未能回到主界面，请检查")
                return
            else:
                img = self.controller.screenshot()
                w, h = img.size
                self.controller.tap(w//3, h//3)
                self.log_signal.emit("点击屏幕（任意处）")
                time.sleep(2)
                self.click_btn(back_btn, threshold)  # 尝试返回主界面
                self.log_signal.emit("尝试返回主界面")
                img = self.controller.screenshot()
                if find_template(img, main_template, threshold=threshold):
                    self.log_signal.emit("已回到主界面，打工任务未完成")
                    self.finished_signal.emit(True)
                else:
                    self.log_signal.emit("未能回到主界面，请检查")
                    self.finished_signal.emit(False)
                return
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
