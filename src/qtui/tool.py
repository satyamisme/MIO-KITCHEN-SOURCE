import sys
import time

from PyQt6.QtCore import Qt, QTimer, QMimeData
from PyQt6.QtGui import QTextCursor, QFont, QDropEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QTabWidget, QLabel, QWidget, \
    QPlainTextEdit



# Custom Controls
class DropLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("border: 2px dashed grey;")
        self.on_drop = lambda text:print(text)

    def set_drop_func(self, func:callable):
        if func.__code__.co_argcount != 1:
            print(f"Set drop func fail!\nThe arg_count of {func.__name__} must be 1, but its {func.__code__.co_argcount}")
        self.on_drop = func

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event:QDropEvent):
        self.on_drop(event.mimeData())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("Left button pressed")
        elif event.button() == Qt.MouseButton.RightButton:
            print("Right button pressed")

# Main Class
class Tool(QMainWindow):
    def __init__(self):
        super(Tool, self).__init__()
        self.log_output = None
        self.timers = set()
        self.setWindowTitle('MIO-KITCHEN')
        self.main_layout = QHBoxLayout()
        self.log_area = QVBoxLayout()
        self.func_area = QVBoxLayout()
        self.main_layout.addLayout(self.log_area)
        self.main_layout.addLayout(self.func_area)
        self.log_area_content()
        self.func_area_content()
        self.start_timers()
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def log_area_content(self):
        time_show = QLabel('MIO-KITCHEN')
        ft = QFont()
        ft.setPointSize(18)
        ft.setBold(True)
        time_show.setFont(ft)
        if not self.log_output:
            self.log_output = QPlainTextEdit()
        drag_and_drop = DropLabel("Drop URL / Path / FileName Here.")
        drag_and_drop.setMinimumHeight(80)
        drag_and_drop.setMinimumWidth(240)
        drag_and_drop.set_drop_func(lambda :...)
        self.log_area.addWidget(time_show)
        self.log_area.addWidget(drag_and_drop)
        drag_and_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_show.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_and_drop.setAcceptDrops(True)
        self.log_area.addWidget(self.log_output)
        show_timer = QTimer(self)
        show_timer.timeout.connect(lambda: time_show.setText(time.strftime("%H:%M:%S")))
        self.timers.add(show_timer)

    def func_area_content(self):
        tabs = QTabWidget()
        self.func_area.addWidget(
            tabs
        )
        tabs.setMovable(True)

        for n, color in enumerate(["red", "green", "blue", "yellow"]):
            tabs.addTab(QLabel(color), str(n))

    def start_timers(self):
        for i in self.timers:
            i.start(1000)


class StdoutRedirector:
    def __init__(self, text_widget: QPlainTextEdit, is_error=False):
        self.text_space = text_widget
        self.flush = ...
        self.error = ''
        self.is_error = is_error

    def write(self, string):
        if self.is_error:
            self.error += string
            print(string)
        self.text_space.insertPlainText(string)
        self.text_space.moveCursor(QTextCursor.MoveOperation.End)


def init(args: list):
    if args:
        print(args)
    app = QApplication(sys.argv)
    window = Tool()
    sys.stdout = StdoutRedirector(window.log_output)
    sys.stderr = StdoutRedirector(window.log_output, is_error=True)
    window.show()
    app.exec()


if __name__ == '__main__':
    init([])
