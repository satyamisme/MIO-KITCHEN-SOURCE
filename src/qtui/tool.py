#!/bin/python3
# Copyright (C) 2022-2025 The MIO-KITCHEN-SOURCE Project
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html#license-text
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import platform
import sys
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QDropEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QTabWidget, QLabel, QWidget, \
    QPlainTextEdit, QFileDialog

from src.core import utils
from src.core.utils import v_code, gettype
import toml
cwd_path = utils.prog_path
tool_bin = os.path.join(cwd_path, 'bin', platform.system(), platform.machine())
tool_self = os.path.normpath(os.path.abspath(sys.argv[0]))
temp = os.path.join(cwd_path, "bin", "temp").replace(os.sep, '/')
tool_log = f'{temp}/{time.strftime("%Y%m%d_%H-%M-%S", time.localtime())}_{v_code()}.log'
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(filename)s:%(name)s:%(message)s',
                    filename=tool_log, filemode='w')

class Settings:
    def __init__(self, set_file:str=None):
        super().__init__()
        self.data:dict = {}
        if set_file:
            self.set_file = set_file
        else:
            self.set_file = os.path.join(cwd_path, "bin", "setting.ini")
        if not os.path.exists(self.set_file):
            raise FileNotFoundError(f"{self.set_file} not exist.")
    def load(self):
        with open(self.set_file, 'r', encoding='utf-8') as f:
            self.data = toml.load(f)
            self.data = self.data.get("setting")
            if self.data is None:
                raise ValueError("Settings is empty.")
    def save(self):
        with open(self.set_file, 'w', encoding='utf-8', newline='\n') as f:
            data = {"setting":self.data}
            toml.dump(data, f)
        self.load()

    def get(self, name:str=None):
        return self.data.get(name)

    def set(self, name, value):
        self.data[name] = value
        self.save()

settings = Settings()

# Custom Controls
class DropLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("border: 2px dashed grey;")
        self.on_drop = lambda text: print(text)

    def set_drop_func(self, func: callable):
        if func.__code__.co_argcount < 2:
            logging.warning(
                f"Set drop func fail!\nThe arg_count of {func.__name__} must be 1 or 2(first is self), but its {func.__code__.co_argcount}")
            return 1
        self.on_drop = func
        return None

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event: QDropEvent):
        text = event.mimeData().text()
        if not text:
            return
        if '\n' in text:
            lines = text.split('\n')
        else:
            lines = [text]
        self.on_drop(lines)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            file_name_dialog = QFileDialog()
            file_name_dialog.setWindowTitle("Choose files")
            file_names, _ = file_name_dialog.getOpenFileNames()
            self.on_drop(file_names)


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

    def dnd_file(self, files: list[str]):
        for f in files:
            try:
                if hasattr(f, 'decode'):
                    f = f.decode('gbk')
            except (Exception, BaseException):
                logging.exception("dnd_file:decode")
            if os.path.exists(f):
                file_type = gettype(f)
                if file_type == 'mpk':
                    print("Install Mpk")
                elif file_type not in ['fnf', 'fne', 'unknown']:
                    print("")
                else:
                    print(f"{f}[{file_type}] not supported.")
            elif f.startswith('http'):
                print(f"this is a url{f}")
            else:
                print(self.tr(f'{f} not exist.'))

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
        drag_and_drop.set_drop_func(self.dnd_file)
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
    app = QApplication(sys.argv)
    settings.load()
    window = Tool()
    sys.stdout = StdoutRedirector(window.log_output)
    sys.stderr = StdoutRedirector(window.log_output, is_error=True)
    if args:
        pass
    window.show()
    app.exec()


if __name__ == '__main__':
    init([])
