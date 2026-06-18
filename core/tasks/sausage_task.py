import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template

class SausageTask(BaseTask):
    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行香肠伯任务...")
        threshold = self.config.get("threshold", 0.7)

        # 加载按钮模板
        sausage_btn = self.config.get("sausage_btn", "imgs/sausage_btn.png")
        direct_claim_btn = self.config.get("direct_claim_btn", "imgs/direct_claim_btn.png")
        roll_btn = self.config.get("roll_btn", "imgs/roll_btn.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        # 用户选择的操作：'领取' 或 '掷骰'
        action = self.config.get("action", "领取")  # 默认领取

        # 步骤1: 点击香肠伯按钮
        if not self.click_btn(sausage_btn, threshold):
            self.log_signal.emit("未找到香肠伯按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(2)  # 等待活动页面加载

        # 步骤2: 根据用户设置点击对应按钮
        if action == "领取":
            btn_path = direct_claim_btn
            action_name = "直接领取"
        else:
            btn_path = roll_btn
            action_name = "掷骰"

        if not self.click_btn(btn_path, threshold):
            self.log_signal.emit(f"未找到{action_name}按钮，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit(f"已点击 {action_name}")
        time.sleep(5)  # 等待动画/响应

        # 步骤3: 点击中心偏上1/3处2次
        img = self.controller.screenshot()
        w, h = img.size
        # 中心偏上1/3：y = h/3，x = w/2
        click_x = w // 2
        click_y = h // 3
        for i in range(2):
            self.controller.tap(click_x, click_y)
            self.log_signal.emit(f"点击中心偏上1/3 ({click_x}, {click_y}) 第{i+1}次")
            time.sleep(0.5)

        time.sleep(1)

        # 步骤4: 尝试点击返回按钮两次（以返回主界面）
        for i in range(2):
            self.click_btn(back_btn, threshold, required=False)
            time.sleep(1)

        # 步骤5: 截图确认是否回到主界面
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，香肠伯任务完成")
            self.finished_signal.emit(True)
        else:
            self.log_signal.emit("未能回到主界面，请检查")
            self.finished_signal.emit(False)

    # ---------- 辅助方法 ----------
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