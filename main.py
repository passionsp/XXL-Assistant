import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys
import traceback

def global_exception_handler(exc_type, exc_value, exc_tb):
    with open("crash.log", "a", encoding="utf-8") as f:
        f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    print("程序异常崩溃，详情请查看 crash.log")

sys.excepthook = global_exception_handler
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())