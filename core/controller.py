import time
import adbutils
from PIL import Image

class GameController:
    def __init__(self, device_serial=None):
        self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        if device_serial:
            self.device = self.adb.device(serial=device_serial)
        else:
            devices = self.adb.device_list()
            if not devices:
                raise Exception("未找到 ADB 设备")
            self.device = devices[0]
        print(f"已连接设备: {self.device.serial}")

    def screenshot(self, retry=3):
        for attempt in range(retry):
            try:
                img = self.device.screenshot()
                if img and img.size[0] > 0 and img.size[1] > 0:
                    return img
            except Exception as e:
                print(f"截图失败: {e}, 重试 {attempt+1}/{retry}")
            time.sleep(1.5)
        raise Exception("多次截图失败")

    def tap(self, x, y):
        self.device.click(x, y)
        print(f"点击 ({x}, {y})")
    def swipe(self, start_x, start_y, end_x, end_y, duration=0.5):
        """
        模拟滑动操作
        :param start_x: 起始X坐标
        :param start_y: 起始Y坐标
        :param end_x: 终点X坐标
        :param end_y: 终点Y坐标
        :param duration: 滑动持续时间（秒）
        """
        self.device.swipe(start_x, start_y, end_x, end_y, duration)
        print(f"滑动: ({start_x},{start_y}) -> ({end_x},{end_y}) 耗时{duration}s")