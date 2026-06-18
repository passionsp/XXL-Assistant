import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template

class InviteTask(BaseTask):
    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行召唤任务...")
        threshold = self.config.get("threshold", 0.7)

        # 加载按钮模板
        invite_btn = self.config.get("invite_btn", "imgs/invite_btn.png")
        single_summon_btn = self.config.get("single_summon_btn", "imgs/single_summon_btn.png")
        quxiao_btn = self.config.get("quxiao_summon_btn", "imgs/quxiaozhaohuan_btn.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        # 步骤1: 点击召唤按钮
        if not self.click_btn(invite_btn, threshold):
            self.log_signal.emit("未找到召唤按钮，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("已点击召唤按钮")
        time.sleep(2)

        # 步骤2: 点击单次召唤
        if not self.click_btn(single_summon_btn, threshold):
            self.log_signal.emit("未找到单次召唤按钮，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("已点击单次召唤")
        time.sleep(1)  # 等待弹窗或动画

        # 步骤3: 截图并检测是否有"取消召唤"按钮
        img = self.controller.screenshot()
        if find_template(img, quxiao_btn, threshold=threshold):
            self.log_signal.emit("检测到取消召唤按钮，点击取消")
            self.click_btn(quxiao_btn, threshold, required=False)
            time.sleep(1)
            # 点击取消后，界面可能返回召唤界面，需要再点击返回回到主界面
            self.log_signal.emit("点击返回按钮回到主界面")
            self.click_btn(back_btn, threshold, required=False)
            time.sleep(1)
        else:
            self.log_signal.emit("未检测到取消召唤按钮，执行正常召唤流程")
            # 步骤4: 点击 (70, 120) 两次，再点击 (450, 1510)
            w, h = img.size
            scale_x = w / 900.0
            scale_y = h / 1600.0
            for i in range(2):
                x = int(70 * scale_x)
                y = int(120 * scale_y)
                self.controller.tap(x, y)
                self.log_signal.emit(f"点击 ({x}, {y}) 第{i+1}次")
                time.sleep(0.5)
            x = int(450 * scale_x)
            y = int(1510 * scale_y)
            self.controller.tap(x, y)
            self.log_signal.emit(f"点击 ({x}, {y})")
            time.sleep(1)

        # 步骤5: 确保回到主界面（若未回到，尝试返回）
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，召唤任务完成")
            self.finished_signal.emit(True)
            return
        else:
            self.log_signal.emit("未回到主界面，尝试返回")
            for _ in range(2):
                self.click_btn(back_btn, threshold, required=False)
                time.sleep(1)
                img = self.controller.screenshot()
                if find_template(img, main_template, threshold=threshold):
                    self.log_signal.emit("已回到主界面，召唤任务完成")
                    self.finished_signal.emit(True)
                    return
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