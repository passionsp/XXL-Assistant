import time
import re
from core.tasks.base_task import BaseTask
from core.recognizer import find_template
SPECIAL_NO_PRICE_LIMIT_PRODUCTS = ["银酒铃", "金酒铃", "特卖型录"]
# 商品名称映射：标准名称 -> 匹配关键词列表（OCR 文本包含其中任一关键词即匹配）
PRODUCT_MAPPING = {
    "速通票": ["速通", "速捶", "逮捶", "速捅", "捶", "捅", "票"],
    "征才广告": ["征才", "广告", "广吉"],
    "健身中心入场券": ["健身", "入场券", "中止", "孔场"],
    "困难模式入场券": ["困难", "入场券", "困难模式"],
    "能量大满罐": ["能量", "大满罐", "大满", "满罐", "县","t"],
    "金酒铃": ["金酒", "酒铃", "宝酒轻", "铃","宝酒","宝"],
    "观光工坊入场券": ["观光", "工坊", "了场券"],
    "特卖型录": ["特卖", "型录"],
    "能量饮料": ["能量", "饮料", "饮", "孟"],
    "培欲房卡": ["培欲", "房卡", "培", "尾卡"],
    "入门营养惊喜包": ["入门", "惊喜包", "营养惊喜包", "初", "圾"],  # 覆盖"初圾"
    "进阶营养惊喜包": ["进阶", "惊喜包"],
    "中级营养惊喜包": ["中级", "惊喜包"],
    "心得兑换券": ["心得", "兑换券", "止得", "兑换荐"],
    "空白碎片惊喜包": ["空白", "碎片", "惊喜包"],
    "精华": ["精华", "精", "华"],
    "碎片重洗牌": ["碎片", "碎", "重洗", "洗牌"],
    "符文墨水": ["符文", "墨水", "符", "墨"],
}
ALL_PRODUCT_NAMES = list(PRODUCT_MAPPING.keys())

class ShijiTask(BaseTask):
    def __init__(self, controller, config=None):
        super().__init__(controller, config)
        if not hasattr(ShijiTask, 'ocr'):
            import ddddocr
            ShijiTask.ocr = ddddocr.DdddOcr(use_gpu=False)
        self.ocr = ShijiTask.ocr

    def run(self):
        if not self.ensure_main_screen():
            self.log_signal.emit("无法回到主界面，任务终止")
            self.finished_signal.emit(False)
            return
        self.log_signal.emit("开始执行市集任务...")
        threshold = self.config.get("threshold", 0.7)

        # 按钮模板
        shiji_btn = self.config.get("shiji_btn", "imgs/shiji_btn.png")
        goumai_btn = self.config.get("goumai_btn", "imgs/goumai_btn.png")
        shuaxin_btn = self.config.get("shuaxin_btn", "imgs/shuaxin_btn.png")
        piaojuan_shuaxin_btn = self.config.get("piaojuan_shuaxin_btn", "imgs/piaojuan_shuaxin_btn.png")
        quxiao_btn = self.config.get("quxiao_btn", "imgs/quxiao_btn.png")
        back_btn = self.config.get("back_btn", "imgs/back_btn.png")
        main_template = self.config.get("main_template", "imgs/main_screen.png")

        # 商品配置
        products_config = self.config.get("products", {})
        if not products_config:
            for name in ALL_PRODUCT_NAMES:
                products_config[name] = {"enabled": True, "max_price": 0}
            self.config["products"] = products_config
            self.log_signal.emit("警告：未配置商品设置，使用默认（全部禁用）")

        # 生成15个商品区域
        product_regions = []
        for row in range(3):
            y_name = 680 + row * 230
            y_price = y_name + 40
            for col in range(5):
                x_name = 20 + col * 180
                x_price = x_name + 35
                product_regions.append({
                    "name_region": [x_name, y_name, 140, 20],
                    "price_region": [x_price, y_price, 105, 20]
                })

        # 点击市集按钮
        if not self.click_btn(shiji_btn, threshold):
            self.log_signal.emit("未找到市集按钮，任务终止")
            self.finished_signal.emit(False)
            return
        time.sleep(2)

        max_loops = self.config.get("max_loops", 30)
        for loop in range(max_loops):
            self.log_signal.emit(f"市集循环 {loop+1}/{max_loops}")
            img = self.controller.screenshot()
            # 调试输出所有商品识别结果
            self.log_signal.emit("---- 当前市集商品识别结果 ----")
            for idx, regions in enumerate(product_regions, start=1):
                # 获取处理后文本
                name_text = self.ocr_region(img, regions["name_region"])
                price_text = self.ocr_region(img, regions["price_region"])
                # 获取原始文本（用于调试）
                raw_name = self.ocr_raw(img, regions["name_region"])
                raw_price = self.ocr_raw(img, regions["price_region"])
                self.log_signal.emit(f"商品{idx:2d}: 名称='{name_text}' (原始:'{raw_name}'), 价格='{price_text}' (原始:'{raw_price}')")
            self.log_signal.emit("--------------------------------------")
            # ---- 第一次扫描 ----
            found = False
            for regions in product_regions:
                if self.check_and_buy_product(img, regions, products_config, threshold, goumai_btn):
                    found = True
                    break
            if found:
                continue  # 购买了商品，重新扫描

            # ---- 二次确认（避免OCR误判） ----
            self.log_signal.emit("第一次扫描无可购买商品，进行二次确认...")
            img2 = self.controller.screenshot()
            found2 = False
            for regions in product_regions:
                if self.check_and_buy_product(img2, regions, products_config, threshold, goumai_btn):
                    found2 = True
                    break
            if found2:
                continue  # 二次确认后购买了商品，继续循环

            # ---- 二次确认仍无可购买商品，刷新 ----
            self.log_signal.emit("二次确认无可购买商品，尝试刷新")
            # 检测票券刷新弹窗
            img = self.controller.screenshot()
            # ---- 点击刷新后，用OCR判断是否出现票券刷新弹窗 ----
            self.log_signal.emit("点击刷新按钮")
            if not self.click_btn(shuaxin_btn, threshold, required=False):
                self.log_signal.emit("未找到刷新按钮，结束任务")
                break
            time.sleep(1)

            img = self.controller.screenshot()
            # 获取OCR区域（可配置）
            piaojuan_region = self.config.get("piaojuan_ocr_region", [580,840,30,20])
            ocr_text = self.ocr_region(img, piaojuan_region)  # 使用已有的ocr_region方法

            # 判断是否出现"票券刷新"（识别到数字1或包含"票券"）
            if "1" in ocr_text or "票券" in ocr_text:
                self.log_signal.emit(f"检测到票券刷新弹窗 (OCR识别: '{ocr_text}')，点击刷新")
                # 点击刷新按钮（可以用模板，也可以用坐标；这里用模板确保准确）
                self.click_btn(piaojuan_shuaxin_btn, threshold)
                time.sleep(2)
                continue  # 刷新后重新循环
            else:
                self.log_signal.emit(f"未检测到票券刷新 (OCR识别: '{ocr_text}')，点击取消")
                self.click_btn(quxiao_btn, threshold, required=False)
                time.sleep(1)
                break

        # 返回主界面
        self.log_signal.emit("点击返回按钮离开市集")
        self.click_btn(back_btn, threshold)
        time.sleep(1)
        img = self.controller.screenshot()
        if find_template(img, main_template, threshold=threshold):
            self.log_signal.emit("已回到主界面，市集任务完成")
            self.finished_signal.emit(True)
        else:
            self.log_signal.emit("未能回到主界面，请检查")
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

    def ocr_region(self, img, region):
        x, y, w, h = region
        cropped = img.crop((x, y, x+w, y+h))
        gray = cropped.convert('L')
        bw = gray.point(lambda p: 255 if p > 150 else 0)
        try:
            res = self.ocr.classification(bw)
            # 修正常见误识别
            res = res.replace('z', '2').replace('Z', '2')
            res = res.replace('o', '0').replace('O', '0').replace('l', '1').replace('I', '1').replace('s', '5')
            res = res.replace('q','0')
            res = res.replace('s', '5')
            return res.strip()
        except Exception as e:
            self.log_signal.emit(f"OCR识别异常: {e}")
            return ""

    def match_product_name(self, ocr_text):
        if not ocr_text:
            return None
        for std_name, keywords in PRODUCT_MAPPING.items():
            for kw in keywords:
                if kw in ocr_text:
                    return std_name
        return None

    def parse_price(self, price_text):
        if not price_text:
            return None
        numbers = re.findall(r'\d+', price_text)
        if numbers:
            return int(numbers[0])
        return None

    def check_and_buy_product(self, img, regions, products_config, threshold, goumai_btn):
        """
        对指定的商品区域进行OCR识别、匹配、价格判断。
        如果符合购买条件，则点击商品并点击购买按钮，返回True；否则返回False。
        """
        name_text = self.ocr_region(img, regions["name_region"])
        price_text = self.ocr_region(img, regions["price_region"])
        if not name_text:
            return False

        matched = self.match_product_name(name_text)
        if not matched:
            return False

        if matched not in products_config:
            return False
        cfg = products_config[matched]
        if not cfg.get("enabled", False):
            return False

        # 解析价格
        price_num = self.parse_price(price_text)
        if price_num is None:
            self.log_signal.emit(f"商品 {matched} 价格无法识别: '{price_text}'，跳过")
            return False

        max_price = cfg.get("max_price", -1)

        # 特殊商品：价格 ≤ 阈值 或 价格 ≥ 10000 则购买
        if matched in SPECIAL_NO_PRICE_LIMIT_PRODUCTS:
            if price_num <= max_price or price_num >= 10000:
                self.log_signal.emit(f"特殊商品 {matched} 符合条件 (价格{price_num} ≤ {max_price} 或 ≥ 10000)，购买")
            else:
                self.log_signal.emit(f"特殊商品 {matched} 价格{price_num} 不在可购买区间，跳过")
                return False
        else:
            # 普通商品：只买价格 ≤ 阈值的
            if max_price == -1:
                return False
            if price_num > max_price:
                self.log_signal.emit(f"商品 {matched} 价格{price_num} > {max_price}，不购买")
                return False

        # 执行购买
        self.log_signal.emit(f"找到可购买商品: {matched} (价格{price_num})")
        x, y, w, h = regions["name_region"]
        self.controller.tap(x + w//2, y + h//2)
        time.sleep(1)
        if not self.click_btn(goumai_btn, threshold, required=False, timeout=3):
            self.log_signal.emit("未找到购买按钮，可能已售罄，跳过此商品")
            return False
        else:
            self.log_signal.emit("已点击购买按钮")
            time.sleep(1)
            self.controller.tap(img.size[0]//3, img.size[1]//3)  # 点击确认购买
            time.sleep(1)
            return True
    def ocr_raw(self, img, region):
        """
        返回指定区域的原始 OCR 识别结果（不进行字符替换）
        """
        x, y, w, h = region
        cropped = img.crop((x, y, x+w, y+h))
        gray = cropped.convert('L')
        bw = gray.point(lambda p: 255 if p > 150 else 0)
        try:
            return self.ocr.classification(bw).strip()
        except Exception:
            return ""