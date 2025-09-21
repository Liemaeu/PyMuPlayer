# PyMu Player - A simple cross-platform music player
# Copyright (C) 2025 Richard Knausenberger
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from PyQt6.QtCore import (
    QEvent,
    QObject,
    QSettings,
    QUrl,
    Qt,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)
import sys

EXTENSIONS = {".aac", ".aif", ".aiff", ".flac", ".mp3", ".ogg", ".wav"}
HOME = str(Path.home())
MIN_WIDTH = 300
SPACER_LARGE = 30
SPACER_MEDIUM = 12
SPACER_SMALL = 2

class SliderClick(QObject):
    """Click on QSlider"""
    def __init__(self, slider, callback):
        super().__init__()
        self.slider = slider
        self.callback = callback

    def eventFilter(self, obj, event):
        if obj == self.slider:
            if event.type() == QEvent.Type.Wheel:
                return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.slider.orientation() == Qt.Orientation.Horizontal:
                    pos = event.position().x()
                    value = round(
                        pos / self.slider.width()
                        * (self.slider.maximum() - self.slider.minimum())
                    )
                else:
                    pos = event.position().y()
                    value = round(
                        (1 - pos / self.slider.height())
                        * (self.slider.maximum() - self.slider.minimum())
                    )
                self.callback(value)
        return False

settings = QSettings("PyMuPlayer")
location = settings.value("location", HOME)
volume = settings.value("volume", 100, type=int)

def save_setting(name: str, value: any):
    """Save a setting"""
    settings.setValue(name, value)

def verify_location():
    """Check if the location is valid"""
    global location
    if not Path(location).is_dir():
        location = HOME
        save_setting("location", location)

verify_location()
current = 0
entries = [
    file
    for file in Path(location).iterdir()
    if not file.name.startswith(".") and (
        file.is_dir() or file.suffix.lower() in EXTENSIONS
    )
]
entries_sorted = sorted(
    entries, key=lambda f: (not f.is_dir(), f.name.lower())
)

files = [f.name for f in entries_sorted]
index = -1
is_muted = False
is_playing = False
length = 0
title = ""

# App
app = QApplication(sys.argv)
window = QMainWindow()
icon = QIcon(str(Path(__file__).parent / "Icon.png"))
app.setWindowIcon(icon)
window.setWindowIcon(icon)

if not settings.value("geometry"):
    screen = app.primaryScreen().size()
    width = int(screen.width() * 2/3)
    height = int(screen.height() * 2/3)
    window.resize(width, height)
else:
    window.restoreGeometry(settings.value("geometry"))

def save_window_geometry():
    """Save the window size"""
    save_setting("geometry", window.saveGeometry())

def change_volume(new_volume: int):
    """Change the volume"""
    global volume
    volume = new_volume
    output.setVolume(volume / 100)
    volume_bar.setValue(volume)
    save_setting("volume", volume)

def update_length_label():
    """Update the length label text"""
    length_label.setText(format_time(length))

def update_length(time: int):
    """Update the length value"""
    global length
    length = int(time / 1000)
    update_length_label()
    time_bar.setMaximum(length)

def update_current_label():
    """Update the current time label text"""
    current_label.setText(format_time(current))

def update_current(time: int):
    """Update the current time value"""
    global current
    current = int(time / 1000)
    update_current_label()
    time_bar.setValue(current)

# Media player
output = QAudioOutput()
player = QMediaPlayer()
player.setAudioOutput(output)
player.durationChanged.connect(update_length)
player.positionChanged.connect(update_current)
player.mediaStatusChanged.connect(lambda status: finished(status))

def previous():
    """Back button"""
    if index > 0:
        files_list.setCurrentRow(index - 1)
        double_click(files_list.currentItem())

def stop():
    """Stop button"""
    global index, is_playing, title
    player.stop()
    is_playing = False
    update_play_pause_icon()
    play_pause_button.setEnabled(False)
    stop_button.setEnabled(False)
    title = ""
    index = -1
    update_window_title()
    update_length(0)
    update_current(0)
    update_skip_buttons()

def play():
    """Play an audio file"""
    global is_playing
    player.play()
    is_playing = True
    update_play_pause_icon()

def play_pause():
    """"Play/Pause button"""
    global is_playing
    if is_playing:
        player.pause()
        is_playing = False
        update_play_pause_icon()
    else:
        play()

def update_play_pause_icon():
    """Update the play/pause button icon"""
    play_pause_button.setIcon(window.style().standardIcon(
        QStyle.StandardPixmap.SP_MediaPause if is_playing
        else QStyle.StandardPixmap.SP_MediaPlay)
    )

def next():
    """Skip forward button"""
    if index < files_list.count() - 1:
        files_list.setCurrentRow(index + 1)
        double_click(files_list.currentItem())

def format_time(seconds: int) -> str:
    """Format the time to hh:mm:ss"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def change_time(time: int):
    """Change the value of the time bar"""
    player.setPosition(time * 1000)

def update_location_label():
    """Update the location label text"""
    max_width = (
        window.width()
        - home_button.sizeHint().width()
        - refresh_button.sizeHint().width()
        - up_button.sizeHint().width()
        - mute_button.sizeHint().width()
        - SPACER_MEDIUM * 2
    )
    max_width = max(MIN_WIDTH, max_width)
    text = location_label.fontMetrics().elidedText(
        location, Qt.TextElideMode.ElideLeft, max_width
    )
    location_label.setText(text)
    location_label.setToolTip(location)


def update_mute_icon():
    """Update the mute button icon"""
    mute_button.setIcon(window.style().standardIcon(
        QStyle.StandardPixmap.SP_MediaVolumeMuted if is_muted
        else QStyle.StandardPixmap.SP_MediaVolume
    ))

def mute():
    """Mute the volume"""
    global is_muted
    is_muted = not is_muted
    update_mute_icon()
    output.setMuted(is_muted)

def update_files():
    """Update the files in the list"""
    verify_location()
    files_list.clear()
    entries = [
        file for file in Path(location).iterdir()
        if not file.name.startswith(".") and (
            file.is_dir() or file.suffix.lower() in EXTENSIONS
        )
    ]
    entries_sorted = sorted(
        entries, key=lambda f: (not f.is_dir(), f.name.lower())
    )
    for file in entries_sorted:
        files_list.addItem(file.name)

def change_location():
    """Change the location"""
    save_setting("location", location)
    update_files()
    update_location_label()

def home():
    """Home button"""
    global location
    location = HOME
    change_location()

def go_up():
    """Up button"""
    global location
    location = str(Path(location).parent)
    change_location()

def update_window_title():
    """Change the window title according to the played audio files name"""
    name = title.rsplit(".", 1)[0] if "." in title else title
    window.setWindowTitle("PyMu Player" + (" - " + name if title else ""))

def double_click(item: QListWidgetItem):
    """Handle a double click on an audio file or folder"""
    global index, location, title
    selected = Path(location) / item.text()
    if selected.is_dir():
        location = str(selected)
        change_location()
    else:
        player.setSource(QUrl.fromLocalFile(str(selected)))
        title = selected.name
        update_window_title()
        play_pause_button.setEnabled(True)
        stop_button.setEnabled(True)
        files_list.setCurrentItem(item)
        index = files_list.currentRow()
        play()
        update_skip_buttons()

def update_skip_buttons():
    """Update the skip buttons"""
    back_button.setEnabled(False)
    forward_button.setEnabled(False)
    if index == -1:
        return
    if index > 0:
        back_button.setEnabled(True)
    if index < files_list.count() - 1:
        forward_button.setEnabled(True)


def finished(status):
    """Finished playing an audio file"""
    if status == QMediaPlayer.MediaStatus.EndOfMedia:
        next()

# Top bar
back_button = QPushButton()
back_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_MediaSkipBackward
))
back_button.clicked.connect(previous)
back_button.setEnabled(False)
stop_button = QPushButton()
stop_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_MediaStop
))
stop_button.clicked.connect(stop)
stop_button.setEnabled(False)
play_pause_button = QPushButton()
update_play_pause_icon()
play_pause_button.clicked.connect(play_pause)
forward_button = QPushButton()
forward_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_MediaSkipForward
))
forward_button.clicked.connect(next)
forward_button.setEnabled(False)
current_label = QLabel(format_time(current))
time_bar = QSlider(
    minimum = 0, maximum = length, value = current,
    orientation = Qt.Orientation.Horizontal
)
time_bar.setMinimumWidth(MIN_WIDTH)
time_bar.sliderMoved.connect(change_time)
time_bar_click = SliderClick(time_bar, lambda t: change_time(t))
time_bar.installEventFilter(time_bar_click)
length_label = QLabel()
update_length_label()
top_bar = QHBoxLayout()
top_bar.addWidget(back_button)
top_bar.addWidget(stop_button)
top_bar.addWidget(play_pause_button)
top_bar.addWidget(forward_button)
top_bar.addSpacing(SPACER_LARGE)
top_bar.addWidget(current_label)
top_bar.addSpacing(SPACER_SMALL)
top_bar.addWidget(time_bar)
top_bar.addSpacing(SPACER_SMALL)
top_bar.addWidget(length_label)

# Volume settings
mute_button = QPushButton()
update_mute_icon()
mute_button.clicked.connect(mute)
volume_bar = QSlider(minimum = 0, maximum = 100, value = volume)
volume_bar.sliderMoved.connect(change_volume)
volume_bar_click = SliderClick(volume_bar, lambda v: change_volume(v))
volume_bar.installEventFilter(volume_bar_click)
change_volume(volume)
volume_settings = QVBoxLayout()
volume_settings.addWidget(mute_button)
volume_settings.addWidget(volume_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

# Folder navigation bar
home_button = QPushButton()
home_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_DirHomeIcon)
)
home_button.clicked.connect(home)
refresh_button = QPushButton()
refresh_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_BrowserReload
))
refresh_button.clicked.connect(update_files)
up_button = QPushButton()
up_button.setIcon(window.style().standardIcon(
    QStyle.StandardPixmap.SP_ArrowUp
))
up_button.clicked.connect(go_up)
location_label = QLabel()
location_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
folder_navigation_bar = QHBoxLayout()
folder_navigation_bar.addWidget(home_button)
folder_navigation_bar.addWidget(refresh_button)
folder_navigation_bar.addWidget(up_button)
folder_navigation_bar.addSpacing(SPACER_MEDIUM)
folder_navigation_bar.addWidget(
    location_label, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter
)
folder_navigation_bar.addSpacing(SPACER_MEDIUM)

# Folder view
files_list = QListWidget()
files_list.setMinimumHeight(300)
for file in files:
    files_list.addItem(file)
files_list.itemDoubleClicked.connect(double_click)
update_location_label()
folder_view = QVBoxLayout()
folder_view.addLayout(folder_navigation_bar)
folder_view.addWidget(files_list)

# Main content
main_content = QHBoxLayout()
main_content.addLayout(folder_view)
main_content.addLayout(volume_settings)

# Window
update_window_title()
layout = QVBoxLayout()
layout.addLayout(top_bar)
layout.addLayout(main_content)
widget = QWidget()
widget.setLayout(layout)
window.setCentralWidget(widget)
window.show()
app.aboutToQuit.connect(save_window_geometry)

app.exec()