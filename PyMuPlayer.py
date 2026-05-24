# PyMu Player - A simple cross-platform music player
# Copyright (C) 2026 Richard Knausenberger
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
    QCoreApplication,
    QEvent,
    QObject,
    QSettings,
    QTimer,
    QTranslator,
    QUrl,
    Qt,
)
from PyQt6.QtGui import (
    QAction,
    QDesktopServices,
    QIcon,
    QKeySequence,
    QPixmap,
    QShortcut,
)
from PyQt6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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

AUTHOR = "Richard Knausenberger"
BUG_REPORT_URL = "https://github.com/Liemaeu/PyMuPlayer/issues/new"
COPYRIGHT_YEARS = "2025"
DELAY = 1500
EMAIL = "liemaeu@gmail.com"
EXTENSIONS = {".aac", ".aif", ".aiff", ".flac", ".mp3", ".ogg", ".wav"}
HOME = str(Path.home())
LICENSE = "https://www.gnu.org/licenses/gpl-3.0.html.en"
LICENSE_NAME = "GPL-3.0"
LINK_URL = "https://github.com/Liemaeu/PyMuPlayer"
MIN_WIDTH = 300
SEEK_STEP = 10
SPACER_LARGE = 30
SPACER_MEDIUM = 12
SPACER_SMALL = 2
VERSION = "Version 1.0"
VOLUME_STEP = 5

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

# App
app = QApplication(sys.argv)
window = QMainWindow()
icon = QIcon(str(Path(__file__).parent / "Icon.png"))
app.setWindowIcon(icon)
window.setWindowIcon(icon)

# Lanugage
language = language = settings.value("language", "en")

def add_translator():
    """Add a translator"""
    global language, translator
    app.removeTranslator(translator)
    translator = QTranslator()
    if translator.load(f"translations_{language}.qm"):
        app.installTranslator(translator)

# Translation
translator = QTranslator()
add_translator()

def save_settings():
    """Save the settings of the settings window"""
    global language, is_delay
    save_setting("language", settings_language_combo_box.currentData())
    save_setting("delay", settings_delay_checkbox.isChecked())
    language = settings_language_combo_box.currentData()
    is_delay = settings_delay_checkbox.isChecked()
    update_translation()
    settings_window.close()

def set_language(value: str):
    """Set the value of the language setting"""
    index = settings_language_combo_box.findData(value)
    if index != -1:
        settings_language_combo_box.setCurrentIndex(index)

# Settings
settings_window = QWidget()
settings_window.setWindowTitle(QCoreApplication.translate("Settings", "Settings"))
settings_layout = QVBoxLayout()
settings_language_layout = QHBoxLayout()
settings_language_label = QLabel(QCoreApplication.translate("Settings", "Language") + ":")
settings_language_layout.addWidget(settings_language_label)
settings_language_layout.addSpacing(SPACER_LARGE)
settings_language_combo_box = QComboBox()
settings_language_combo_box.addItem("English", "en")
settings_language_combo_box.addItem("Deutsch", "de")
set_language(settings.value("language", "en"))
settings_language_layout.addWidget(settings_language_combo_box)
settings_layout.addLayout(settings_language_layout)
settings_delay_layout = QHBoxLayout()
settings_delay_label = QLabel(QCoreApplication.translate("Settings", "Delay between Songs") + ":")
settings_delay_layout.addWidget(settings_delay_label)
settings_delay_layout.addSpacing(SPACER_LARGE)
settings_delay_checkbox = QCheckBox()
settings_delay_checkbox.setChecked(settings.value("auto_next_enabled", False, type=bool))
settings_delay_layout.addWidget(settings_delay_checkbox)
settings_layout.addLayout(settings_delay_layout)
settings_buttons_layout = QHBoxLayout()
settings_cancel_button = QPushButton(QCoreApplication.translate("Settings", "Cancel"))
settings_cancel_button.clicked.connect(settings_window.close)
settings_buttons_layout.addWidget(settings_cancel_button)
settings_buttons_layout.addStretch()
settings_save_button = QPushButton(QCoreApplication.translate("Settings", "Save"))
settings_save_button.clicked.connect(save_settings)
settings_buttons_layout.addWidget(settings_save_button)
settings_layout.addLayout(settings_buttons_layout)
settings_window.setLayout(settings_layout)

# About
about_window = QWidget()
about_window.setWindowTitle(QCoreApplication.translate("About", "About"))
about_layout = QVBoxLayout()
about_image = QLabel()
about_image_size = int(app.primaryScreen().size().width() * 0.05)
about_image.setPixmap(QPixmap(str(Path(__file__).parent / "Icon.png")).scaled(
    about_image_size, about_image_size, Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
    )
)
about_layout.addWidget(about_image, alignment=Qt.AlignmentFlag.AlignCenter)
about_layout.addSpacing(SPACER_SMALL)
about_title = QLabel("PyMu Player")
about_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
about_title.setStyleSheet("font-weight: bold")
about_layout.addWidget(about_title)
about_layout.addSpacing(SPACER_SMALL)
about_version = QLabel(VERSION)
about_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
about_layout.addWidget(about_version)
about_layout.addSpacing(SPACER_SMALL)
about_link = QLabel('<a href="' + LINK_URL + '">GitHub</a>')
about_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
about_link.setOpenExternalLinks(True)
about_layout.addWidget(about_link)
about_layout.addSpacing(SPACER_MEDIUM)
about_author = QLabel(QCoreApplication.translate("About", "Author") + ": " + AUTHOR)
about_layout.addWidget(about_author)
about_email = QLabel(
    'Email: <a href="mailto:' + EMAIL + '?subject=PyMu%20Player:">' + EMAIL + '</a>'
)
about_email.setOpenExternalLinks(True)
about_layout.addWidget(about_email)
about_license = QLabel(
    QCoreApplication.translate("About", "License")
    + ': <a href="' + LICENSE + '">' + LICENSE_NAME + '</a>'
)
about_license.setOpenExternalLinks(True)
about_layout.addWidget(about_license)
about_layout.addSpacing(SPACER_SMALL)
about_copyright = QLabel("© " + COPYRIGHT_YEARS)
about_copyright.setStyleSheet("font-style: italic")
about_layout.addWidget(about_copyright)
about_window.setLayout(about_layout)

# Check if a location was passed
if len(sys.argv) > 1:
    arg_location = Path(sys.argv[1]).expanduser().resolve()
    if arg_location.is_dir():
        location = str(arg_location)
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
delay_timer = QTimer()
delay_timer.setSingleShot(True)
is_delay = settings.value("delay", False, type=bool)

def previous():
    """Back button"""
    delay_timer.stop()
    if index > 0:
        files_list.setCurrentRow(index - 1)
        double_click(files_list.currentItem())

def stop():
    """Stop button"""
    global index, is_playing, title
    delay_timer.stop()
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
    delay_timer.stop()
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
    play_pause_button.setToolTip(
        QCoreApplication.translate("App", "Pause (Space, K)") if is_playing 
        else QCoreApplication.translate("App", "Play (Space, K)")
    )

def next():
    """Skip forward button"""
    delay_timer.stop()
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

def seek_forward():
    """Seek forward"""
    player.setPosition(player.position() + SEEK_STEP * 1000)

def seek_backward():
    """Seek backward"""
    player.setPosition(max(0, player.position() - SEEK_STEP *1000))

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

def update_add_remove_button():
    """Update the add/remove button icon"""
    is_bookmark = location in settings.value("bookmarks", [], type=list)
    add_remove_button.setIcon(window.style().standardIcon(
        QStyle.StandardPixmap.SP_TrashIcon if is_bookmark
        else QStyle.StandardPixmap.SP_FileDialogNewFolder)
    )
    add_remove_button.setToolTip(
        QCoreApplication.translate("App", "Remove Bookmark (Ctrl+D)") if is_bookmark
        else QCoreApplication.translate("App", "Add Bookmark (Ctrl+D)")
    )

def open_bookmark(path: str):
    """Open a bookmark location"""
    global location
    if not Path(path).is_dir():
        return
    location = path
    change_location()

def update_bookmark_menu():
    """Update the bookmark menu"""
    bookmark_menu.clear()
    bookmarks = settings.value("bookmarks", [], type=list)
    for path in bookmarks:
        action = QAction(path, window)
        action.triggered.connect(lambda checked=False, p=path: open_bookmark(p))
        bookmark_menu.addAction(action)

def add_remove_bookmark():
    """Add or remove a bookmark"""
    bookmarks = settings.value("bookmarks", [], type=list)
    if location in bookmarks:
        bookmarks.remove(location)
    else:
        bookmarks.append(location)
    save_setting("bookmarks", bookmarks)
    update_bookmark_menu()
    update_add_remove_button()

def update_mute_icon():
    """Update the mute button icon"""
    mute_button.setIcon(window.style().standardIcon(
        QStyle.StandardPixmap.SP_MediaVolumeMuted if is_muted
        else QStyle.StandardPixmap.SP_MediaVolume)
    )
    mute_button.setToolTip(
        QCoreApplication.translate("App", "Un-Mute (M)") if is_muted
        else QCoreApplication.translate("App", "Mute (M)")
    )

def mute():
    """Mute the volume"""
    global is_muted
    is_muted = not is_muted
    update_mute_icon()
    output.setMuted(is_muted)

def volume_up():
    """Increase the volume"""
    new_volume = min(100, volume + VOLUME_STEP)
    change_volume(new_volume)

def volume_down():
    """Decrease the volume"""
    new_volume = max(0, volume - VOLUME_STEP)
    change_volume(new_volume)

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
    update_add_remove_button()

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
    delay_timer.stop()
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
        if is_delay:
            delay_timer.timeout.connect(delay)
            delay_timer.start(DELAY)
        else:
            next()

def delay():
    """Play the next song after delay"""
    delay_timer.timeout.disconnect(delay)
    next()

def show_settings():
    """Open the settings window"""
    global language
    set_language(language)
    settings_delay_checkbox.setChecked(is_delay)
    settings_window.show()
    settings_window.raise_()
    settings_window.activateWindow()

def update_translation():
    """Update the translation"""
    add_translator()
    update_play_pause_icon()
    update_mute_icon()
    back_button.setToolTip(QCoreApplication.translate("App", "Previous (J)"))
    stop_button.setToolTip(QCoreApplication.translate("App", "Stop (S)"))
    forward_button.setToolTip(QCoreApplication.translate("App", "Next (L)"))
    home_button.setToolTip(QCoreApplication.translate("App", "Home (H)"))
    refresh_button.setToolTip(QCoreApplication.translate("App", "Refresh (F5)"))
    up_button.setToolTip(QCoreApplication.translate("App", "Up (Backspace)"))
    update_add_remove_button()
    file_menu.setTitle(QCoreApplication.translate("Menu", "File"))
    settings_action.setText(QCoreApplication.translate("Menu", "Settings"))
    settings_window.setWindowTitle(QCoreApplication.translate("Settings", "Settings"))
    settings_language_label.setText(QCoreApplication.translate("Settings", "Language") + ":")
    settings_delay_label.setText(QCoreApplication.translate("Settings", "Delay between Songs") + ":")
    settings_cancel_button.setText(QCoreApplication.translate("Settings", "Cancel"))
    settings_save_button.setText(QCoreApplication.translate("Settings", "Save"))
    exit_action.setText(QCoreApplication.translate("Menu", "Exit"))
    bookmark_menu.setTitle(QCoreApplication.translate("Menu", "Bookmarks"))
    help_menu.setTitle(QCoreApplication.translate("Menu", "Help"))
    about_action.setText(QCoreApplication.translate("Menu", "About"))
    about_window.setWindowTitle(QCoreApplication.translate("About", "About"))
    about_author.setText(QCoreApplication.translate("About", "Author") + ": " + AUTHOR)
    about_license.setText(
        QCoreApplication.translate("About", "License")
        + ': <a href="' + LICENSE + '">' + LICENSE_NAME + '</a>'
    )
    bug_report_action.setText(QCoreApplication.translate("Menu", "Report a Bug"))

def show_about():
    """Open the about window"""
    about_window.show()
    about_window.raise_()
    about_window.activateWindow()

def report_bug():
    """Report a bug"""
    QDesktopServices.openUrl(QUrl(BUG_REPORT_URL))

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
play_pause_button.setEnabled(False)
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
add_remove_button = QPushButton()
add_remove_button.clicked.connect(add_remove_bookmark)
folder_navigation_bar = QHBoxLayout()
folder_navigation_bar.addWidget(home_button)
folder_navigation_bar.addWidget(refresh_button)
folder_navigation_bar.addWidget(up_button)
folder_navigation_bar.addSpacing(SPACER_MEDIUM)
folder_navigation_bar.addWidget(
    location_label, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter
)
folder_navigation_bar.addSpacing(SPACER_MEDIUM)
folder_navigation_bar.addWidget(add_remove_button)

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

# Menu bar
menu_bar = window.menuBar()
file_menu = menu_bar.addMenu(QCoreApplication.translate("Menu", "File"))
settings_action = file_menu.addAction(QCoreApplication.translate("Menu", "Settings"))
settings_action.triggered.connect(show_settings)
exit_action = file_menu.addAction(QCoreApplication.translate("Menu", "Exit"))
exit_action.triggered.connect(app.quit)
bookmark_menu = menu_bar.addMenu(QCoreApplication.translate("Menu", "Bookmarks"))
update_bookmark_menu()
help_menu = menu_bar.addMenu(QCoreApplication.translate("Menu", "Help"))
about_action = help_menu.addAction(QCoreApplication.translate("Menu", "About"))
about_action.triggered.connect(show_about)
bug_report_action = help_menu.addAction(QCoreApplication.translate("Menu", "Report a Bug"))
bug_report_action.triggered.connect(report_bug)

# Shortcuts
shortcut_back = QShortcut(QKeySequence("J"), window)
shortcut_back.activated.connect(previous)
shortcut_stop = QShortcut(QKeySequence("S"), window)
shortcut_stop.activated.connect(stop)
shortcut_play_pause = QShortcut(QKeySequence("Space"), window)
shortcut_play_pause.activated.connect(play_pause)
shortcut_play_pause_alt = QShortcut(QKeySequence("K"), window)
shortcut_play_pause_alt.activated.connect(play_pause)
shortcut_forward = QShortcut(QKeySequence("L"), window)
shortcut_forward.activated.connect(next)
shortcut_right = QShortcut(QKeySequence("Right"), window)
shortcut_right.activated.connect(seek_forward)
shortcut_left = QShortcut(QKeySequence("Left"), window)
shortcut_left.activated.connect(seek_backward)
shortcut_home = QShortcut(QKeySequence("H"), window)
shortcut_home.activated.connect(home)
shortcut_refresh = QShortcut(QKeySequence("F5"), window)
shortcut_refresh.activated.connect(update_files)
shortcut_up = QShortcut(QKeySequence("Backspace"), window)
shortcut_up.activated.connect(go_up)
shortcut_add_remove = QShortcut(QKeySequence("Ctrl+D"), window)
shortcut_add_remove.activated.connect(add_remove_bookmark)
shortcut_mute = QShortcut(QKeySequence("M"), window)
shortcut_mute.activated.connect(mute)
shortcut_volume_up = QShortcut(QKeySequence("."), window)
shortcut_volume_up.activated.connect(volume_up)
shortcut_volume_down = QShortcut(QKeySequence(","), window)
shortcut_volume_down.activated.connect(volume_down)
shortcut_enter = QShortcut(QKeySequence("Return"), files_list)
shortcut_enter.activated.connect(lambda: double_click(files_list.currentItem()))
shortcut_down = QShortcut(QKeySequence("Down"), window)
shortcut_down.setContext(Qt.ShortcutContext.ApplicationShortcut)
shortcut_down.activated.connect(lambda: files_list.setCurrentRow(
    min(files_list.currentRow() + 1, files_list.count() - 1)
))
shortcut_up = QShortcut(QKeySequence("Up"), window)
shortcut_up.setContext(Qt.ShortcutContext.ApplicationShortcut)
shortcut_up.activated.connect(lambda: files_list.setCurrentRow(
    max(files_list.currentRow() - 1, 0)
))
settings_action.setShortcut(QKeySequence("Ctrl+P"))
exit_action.setShortcut(QKeySequence("Ctrl+Q"))
about_action.setShortcut(QKeySequence("F1"))
shortcut_close_about = QShortcut(QKeySequence("Escape"), about_window)
shortcut_close_about.activated.connect(about_window.close)
shortcut_close_settings = QShortcut(QKeySequence("Escape"), settings_window)
shortcut_close_settings.activated.connect(settings_window.close)
bug_report_action.setShortcut(QKeySequence("Ctrl+Shift+B"))

# Load translation
update_translation()

# Run the app
app.exec()