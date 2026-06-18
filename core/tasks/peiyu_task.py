import time
import re
import os
from core.tasks.base_task import BaseTask
from core.recognizer import find_template

class PeiyuTask(BaseTask):
    def __init__(self, controller, config=None):
        super().__init__(controller, config)
        # 初始化OCR（只做一次）
        if not hasattr(PeiyuTask, 'ocr'):
            import ddddocr
            PeiyuTask.ocr = ddddocr.DdddOcr(use_gpu=False)
        self.ocr = PeiyuTask.ocr

    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行培育任务...")
        threshold = self.config.get("threshold", 0.7)

        # 加载按钮模板
        peiyu_btn = self.config.get("peiyu_btn", "imgs/peiyu_btn.png")
        qihedu_btn = self.config.get("qihedu_btn", "imgs/qihedu_btn.png")
        jinqu_btn = self.config.get("jinqu_btn", "imgs/jinqu_btn.png")
        choupai_btn = self.config.get("choupai_btn", "imgs/choupai_btn.png")
        queding_btn = self.config.get("queding_btn", "imgs/queding_btn.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        # OCR识别区域（道具数量显示在右上角，基于900x1600的绝对坐标）
        item_count_region = self.config.get("item_count_region", [800, 120, 20, 20])  # 示例，需根据实际调整

        # 步骤1: 点击【培育】按钮
        if not self.click_btn(peiyu_btn, threshold):
            self.log_signal.emit("未找到培育按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(2)

        # 步骤2: 点击【契合度结算】按钮
        if not self.click_btn(qihedu_btn, threshold):
            self.log_signal.emit("未找到契合度结算按钮,跳过此步骤")
        time.sleep(1)

        # 步骤3: 点击任意处一次（点屏幕中心）
        img = self.controller.screenshot()
        w, h = img.size
        self.controller.tap(w//2, h//2)
        self.log_signal.emit("点击屏幕中心（任意处）")
        time.sleep(1)

        # 步骤4: 点击【进去玩他】按钮
        if not self.click_btn(jinqu_btn, threshold):
            self.log_signal.emit("未找到进去玩他按钮")
            self.finished_signal.emit(False)
            return
        time.sleep(2)

        # 步骤5: 截图并识别道具数量
        img = self.controller.screenshot()
        item_count = self.get_item_count(img, item_count_region)
        self.log_signal.emit(f"道具数量: {item_count}")

        # 步骤6: 根据道具数量执行分支
        if item_count == 0:
            self.log_signal.emit("道具数量为0，点击返回")
            self.click_btn(back_btn, threshold)
            time.sleep(1)
            
        else:
            self.log_signal.emit(f"道具数量为{item_count}，点击抽牌")
            if not self.click_btn(choupai_btn, threshold):
                self.log_signal.emit("未找到抽牌按钮")
                self.finished_signal.emit(False)
                return
            time.sleep(1)

            # 步骤7: 点击【确定】并点击屏幕中心5次，重复三次
            for i in range(5):
                self.log_signal.emit(f"第{i+1}次确定操作")
                # 点击确定
                if not self.click_btn(queding_btn, threshold):
                    self.log_signal.emit("未找到确定按钮")
                    break
                time.sleep(1)
                # 点击屏幕中心3次
                for _ in range(5):
                    self.controller.tap(w//2, h//2)
                    time.sleep(1)
                self.log_signal.emit(f"第{i+1}次操作完成")
                time.sleep(2)

        # 步骤8: 点击两次返回回到主界面
        self.log_signal.emit("点击返回按钮（第一次）")
        self.click_btn(back_btn, threshold)
        time.sleep(1)
        self.log_signal.emit("点击返回按钮（第二次）")
        self.click_btn(back_btn, threshold)
        time.sleep(1)

        # 步骤9: 检测是否回到主界面
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，培育任务完成")
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

    def get_item_count(self, img, region):
        """
        识别右上角道具数量
        region: [x, y, w, h] 绝对坐标
        """
        x, y, w, h = region
        img_w, img_h = img.size
        if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
            self.log_signal.emit(f"道具区域超出边界: ({x},{y},{w},{h})")
            return 0
        cropped = img.crop((x, y, x + w, y + h))
        # 灰度+二值化
        gray = cropped.convert('L')
        bw = gray.point(lambda p: 255 if p > 150 else 0)
        try:
            result = self.ocr.classification(bw)
            # 修正常见误识别
            result = result.replace('o', '0').replace('O', '0')
            result = result.replace('l', '1').replace('I', '1')
            result = result.replace('z', '2').replace('Z', '2')
            nums = re.findall(r'\d+', result)
            if nums:
                return int(nums[0])
            else:
                self.log_signal.emit(f"道具识别失败，OCR结果: '{result}'")
                return 0
        except Exception as e:
            self.log_signal.emit(f"道具OCR异常: {e}")
            return 0