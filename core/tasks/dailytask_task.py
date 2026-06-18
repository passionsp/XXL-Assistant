import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template

class DailytaskTask(BaseTask):
    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行每日任务...")
        threshold = self.config.get("threshold", 0.7)

        # 加载按钮模板
        task_btn = self.config.get("task_btn", "imgs/task_btn.png")
        yijianlingqu_btn = self.config.get("yijianlingqu_btn", "imgs/yijianlingqu.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        # 绝对坐标（基于 900x1600，如果分辨率不同需缩放）
        exit_x, exit_y = 710, 410
        week_x,week_y=450,1420
        # 步骤1: 点击任务按钮
        if not self.click_btn(task_btn, threshold):
            self.log_signal.emit("未找到任务按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(2)

        # 步骤2: 尝试点击一键领取（可选）
        img = self.controller.screenshot()
        if find_template(img, yijianlingqu_btn, threshold=threshold):
            self.log_signal.emit("找到一键领取按钮，点击")
            self.click_btn(yijianlingqu_btn, threshold, required=False)
            time.sleep(1)
        else:
            self.log_signal.emit("未找到一键领取按钮，跳过")

        # 步骤3: 点击屏幕中心（关闭可能弹出的奖励领取成功提示等）
        w, h = img.size
        self.controller.tap(w // 2, h // 2)
        self.log_signal.emit("点击屏幕中心")
        time.sleep(1)

        # 步骤4: 点击坐标 (710, 40)（退出任务界面的关闭按钮）
        # 这里需要考虑分辨率缩放，如果实际分辨率不是 900x1600，则需缩放
        # 缩放比例：实际宽/900，实际高/1600
        scale_x = w / 900.0
        scale_y = h / 1600.0
        real_x = int(exit_x * scale_x)
        real_y = int(exit_y * scale_y)
        self.controller.tap(real_x, real_y)
        self.log_signal.emit(f"点击活跃奖励 ({real_x}, {real_y})")
        time.sleep(2)

        # 步骤5: 再次点击屏幕中心（关闭可能的提示）
        self.controller.tap(w // 2, h // 2)
        self.log_signal.emit("再次点击屏幕中心")
        time.sleep(3)
        scale_x = w / 900.0
        scale_y = h / 1600.0
        realweek_x = int(week_x * scale_x)
        realweek_y = int(week_y * scale_y)
        self.controller.tap(realweek_x, realweek_y)
        self.log_signal.emit(f"点击每周任务({realweek_x}, {realweek_y})")
        time.sleep(2)  
        img = self.controller.screenshot()
        if find_template(img, yijianlingqu_btn, threshold=threshold):
            self.log_signal.emit("找到一键领取按钮，点击")
            self.click_btn(yijianlingqu_btn, threshold, required=False)
            time.sleep(1)
        else:
            self.log_signal.emit("未找到一键领取按钮，跳过")
        self.log_signal.emit("从右往左点击坐标序列...")
        self.click_coordinates_sequence([
            (710, 420),
            (610, 420),
            (510, 420),
            (410, 420),
            (310, 420)
        ])
        self.controller.tap(w // 2, h // 2)
        time.sleep(2)
        self.click_btn(back_btn, threshold, required=False)
        

        # 步骤8: 检测是否回到主界面
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，每日任务完成")
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
    def click_coordinates_sequence(self, coords):
        """
        按顺序点击一系列坐标（基于900x1600分辨率，自动缩放）
        coords: list of (x, y) 元组
        """
        img = self.controller.screenshot()
        w, h = img.size
        scale_x = w / 900.0
        scale_y = h / 1600.0
        for idx, (x, y) in enumerate(coords, start=1):
            real_x = int(x * scale_x)
            real_y = int(y * scale_y)
            self.controller.tap(real_x, real_y)
            self.log_signal.emit(f"点击坐标 {idx}: ({real_x}, {real_y})")
            time.sleep(0.5)  # 间隔0.5秒，可根据需要调整