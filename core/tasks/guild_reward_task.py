import time
from core.tasks.base_task import BaseTask
from core.recognizer import find_template
import numpy as np
from PIL import Image
import ddddocr
import os
class GuildRewardTask(BaseTask):
    def __init__(self, controller, config=None):
        super().__init__(controller, config)
        self.ocr = ddddocr.DdddOcr(use_gpu=False)  # 如果显卡好可改为 True

    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行公会奖励任务...")
        threshold = self.config.get("threshold", 0.7)
        # 加载配置
        guild_btn = self.config.get("guild_btn", "imgs/guild_btn.png")
        guild_task_btn = self.config.get("guild_task_btn", "imgs/guild_task_btn.png")
        yijianlingqu = self.config.get("claim_all_btn", "imgs/yijianlingqu.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        wishing_well_btn = self.config.get("wishing_well_btn", "imgs/wishing_well_btn.png")
        donate_btn = self.config.get("donate_btn", "imgs/donate_btn.png")
        confirm_donate_btn = self.config.get("confirm_donate_btn", "imgs/confirm_donate_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        sliders = self.config.get("sliders",  [
    {"start": [0.5111, 0.49375], "end": [0.85, 0.49375]},
    {"start": [0.5111, 0.55625], "end": [0.85, 0.55625]},
    {"start": [0.5111, 0.61875], "end": [0.85, 0.61875]},
]
        )

        # OCR区域（星星数量）
        blue_region = self.config.get("blue_star_region")
        purple_region = self.config.get("purple_star_region")
        yellow_region = self.config.get("yellow_star_region")

        # 步骤1: 点击公会
        if not self.click_btn(guild_btn, threshold):
            self.log_signal.emit("未找到公会按钮")
            self.finished_signal.emit(False)
            return
        time.sleep(2)
        
        w, h = self.controller.screenshot().size
        self.controller.tap(w//2, h//2)
        # 步骤2: 点击工会任务
        if not self.click_btn(guild_task_btn, threshold):
            self.log_signal.emit("未找到工会任务按钮")
            if self.click_btn(guild_btn, threshold):  # 尝试返回主界面
                self.log_signal.emit("已进入工会任务界面")
            else:
                self.finished_signal.emit(False)
                return
        time.sleep(2)

        img = self.controller.screenshot()
        if self.find_btn(yijianlingqu, threshold):
            self.click_btn(yijianlingqu, threshold, required=False)
            
        else:
            self.log_signal.emit("未检测到一键领取按钮，直接返回")
        # 无论是否点击，都点击返回
        w,h = img.size
        self.controller.tap(w//2, h//2)
        time.sleep(2)
        self.click_btn(back_btn, threshold)
        time.sleep(1)

        # 哎呦我这傻逼ai在这多写一个步骤4: 返回害我排查半天
        
        

        # 步骤5: 点击许愿池
        img = self.controller.screenshot()
        self.log_signal.emit("正在寻找许愿池按钮...")
        wishing_found = False
        for attempt in range(5):  # 重试5次
            img = self.controller.screenshot()
            pos = find_template(img, wishing_well_btn, threshold=threshold)
            if pos:
                self.controller.tap(pos[0], pos[1])
                self.log_signal.emit("已点击许愿池按钮")
                wishing_found = True
                break
            self.log_signal.emit(f"未找到许愿池按钮，重试 {attempt+1}/5")
            time.sleep(1)
        if not wishing_found:
            self.log_signal.emit("错误：无法找到许愿池按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(5)
        img = self.controller.screenshot()
        blue = self.get_star_count(img, blue_region, "蓝星")
        purple = self.get_star_count(img, purple_region, "紫星")
        yellow = self.get_star_count(img, yellow_region, "黄星")
        self.log_signal.emit(f"初始星星数量: 蓝={blue}, 紫={purple}, 黄={yellow}")

        if blue == 0 and purple == 0 and yellow == 0:
            self.log_signal.emit("所有星星均为0，直接返回主界面，任务结束")
            # 返回公会界面再返回主界面（点击返回两次）
            self.click_btn(back_btn, threshold)
            time.sleep(1)
            self.click_btn(back_btn, threshold)
            time.sleep(1)
            # 判断是否回到主界面
            img = self.controller.screenshot()
            if find_template(img, main_template, threshold=threshold):
                self.log_signal.emit("已回到主界面，任务完成")
                self.finished_signal.emit(True)
            else:
                self.log_signal.emit("未能回到主界面")
                self.finished_signal.emit(False)
            return

        # 步骤6: 捐赠循环
        max_loops = self.config.get("max_donate_loops", 10)
        for loop in range(max_loops):
            self.log_signal.emit(f"捐赠循环 {loop+1}/{max_loops}")

            # 点击捐赠按钮（进入滑动条界面）
            if not self.click_btn(donate_btn, threshold):
                self.log_signal.emit("未找到捐赠按钮，退出循环")
                break
            time.sleep(1)

            # 依次拖动三个滑块（使用固定坐标，每个滑块重复拖动3次确保拖到最右）
            for idx, slider in enumerate(sliders):
                self.drag_slider_by_coords(slider["start"], slider["end"], repeat=1)
                time.sleep(0.5)

            # 点击确认捐赠
            if not self.click_btn(confirm_donate_btn, threshold):
                self.log_signal.emit("未找到确认捐赠按钮")
                break
            time.sleep(1)

            # 点击屏幕中心（关闭可能弹窗）
            img = self.controller.screenshot()
            w, h = img.size
            self.controller.tap(w//3, h//3)
            time.sleep(2)

            # 判断是否继续捐赠
            img = self.controller.screenshot()
            has_donate = self.find_btn(donate_btn, threshold) is not None
            if not has_donate:
                self.log_signal.emit("捐赠按钮消失，停止循环")
                break

            blue = self.get_star_count(img, blue_region, "蓝星")
            purple = self.get_star_count(img, purple_region, "紫星")
            yellow = self.get_star_count(img, yellow_region, "黄星")
            self.log_signal.emit(f"剩余星星: 蓝{blue} 紫{purple} 黄{yellow}")
            if blue == 0 and purple == 0 and yellow == 0:
                self.log_signal.emit("所有星星为0，停止捐赠")
                break

        # 步骤7: 返回公会主界面
        self.click_btn(back_btn, threshold)
        time.sleep(1)
        self.click_btn(back_btn, threshold)
        time.sleep(1)

        # 步骤8: 判断是否回到主界面
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，任务完成")
            self.finished_signal.emit(True)
        else:
            self.log_signal.emit("未能回到主界面")
            self.finished_signal.emit(False)

    # ========== 辅助方法 ==========
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

    def find_btn(self, template_path, threshold):
        img = self.controller.screenshot()
        return find_template(img, template_path, threshold=threshold)

    def drag_slider_by_coords(self, start_ratio, end_ratio, repeat=3):
        """
        使用固定坐标比例拖动滑块
        start_ratio: [x_ratio, y_ratio]
        end_ratio: [x_ratio, y_ratio]
        repeat: 重复拖动次数（确保拖到最右）
        """
        img = self.controller.screenshot()
        w, h = img.size
        start_x = int(w * start_ratio[0])
        start_y = int(h * start_ratio[1])
        end_x = int(w * end_ratio[0])
        end_y = int(h * end_ratio[1])
        for _ in range(repeat):
            self.controller.swipe(start_x, start_y, end_x, end_y, duration=0.3)
            time.sleep(0.3)
        self.log_signal.emit(f"拖动滑块 ({start_x},{start_y}) -> ({end_x},{end_y}) 重复{repeat}次")

    def get_star_count(self, img, region, star_name):
        """
        region: [x, y, width, height] 绝对像素坐标
        """
        x, y, w, h = region
        img_w, img_h = img.size
        if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
            self.log_signal.emit(f"{star_name} 区域超出边界: ({x},{y},{w},{h}) 图像({img_w},{img_h})")
            return 0

        cropped = img.crop((x, y, x + w, y + h))
        
        # 可选：保存调试图片
        # cropped.save(f"debug_{star_name}.png")

        # ddddocr 直接识别 PIL Image 或 bytes
        try:
            # 先转为灰度并二值化可提高准确率（可选）
            gray = cropped.convert('L')
            # 二值化（阈值可调）
            bw = gray.point(lambda p: 255 if p > 150 else 0)
            # 识别
            res = self.ocr.classification(bw)   # 返回字符串，如 "123"
            # 提取数字（有时会附带其他字符）
            res = res.replace('o', '0').replace('O', '0')
            import re
            nums = re.findall(r'\d+', res)
            if nums:
                return int(nums[0])
            else:
                self.log_signal.emit(f"{star_name} 识别失败：'{res}'")
                return 0
        except Exception as e:
            self.log_signal.emit(f"{star_name} OCR异常: {e}")
            return 0