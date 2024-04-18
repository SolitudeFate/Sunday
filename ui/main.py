import os
from threading import Thread

from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox
from qt_material import apply_stylesheet, QtStyleTools

from music_research import music_research
from ui.widget_slots.slots import add_all_items, find_data_song, find_test_song


class MainPage(QMainWindow, QtStyleTools):

    def __init__(self):
        super().__init__()
        self.main = QUiLoader().load('Index.ui')

        # 设置默认主题
        apply_stylesheet(app, theme='dark_yellow.xml')

        # 切换所有默认主题
        self.add_menu_theme(self.main, self.main.menuStyles)
        # 切换Density
        self.add_menu_density(self.main, self.main.menuDensity)

        # 创建新主题
        # self.show_dock_theme(self.main)

        # 读取文件，加载所有下拉选项
        add_all_items(self.main.comboBox1)

        self.main.button1.clicked.connect(self.play_test_song)
        self.main.button2.clicked.connect(self.research_music)
        self.main.button3.clicked.connect(self.play_research_song)

        # 保持视角随光标移动
        self.main.textEdit.textChanged.connect(lambda: self.main.textEdit.ensureCursorVisible())

    # 播放需要识别的歌曲
    def play_test_song(self):
        index = self.main.comboBox1.currentIndex()
        if index != 0:
            test_song_name = self.main.comboBox1.currentText()
            test_song_path = find_test_song(test_song_name)
            thread = Thread(target=self.open_music_player, args=(test_song_path,))
            thread.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要选择歌曲才能播放!')
            msg_box.exec_()

    # 打开媒体播放器
    def open_music_player(self, test_song_path):
        os.startfile(test_song_path)

    # 开始识别
    def research_music(self):
        self.main.lineEdit.setText('')
        self.main.textEdit.setText('')
        index = self.main.comboBox1.currentIndex()
        if index != 0:
            test_song_name = self.main.comboBox1.currentText()
            test_song_path = find_test_song(test_song_name)
            thread = Thread(target=music_research, args=(test_song_path, self))
            thread.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要选择歌曲才能开始识别!')
            msg_box.exec_()

    # 播放识别后的歌曲
    def play_research_song(self):
        research_song_name = self.main.lineEdit.text()

        if research_song_name != '':
            research_song_path = find_data_song(research_song_name)
            thread = Thread(target=self.open_music_player, args=(research_song_path,))
            thread.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要等待歌曲识别出结果后才能播放!')
            msg_box.exec_()


app = QApplication([])
app.setWindowIcon(QIcon('Images/logo.jpg'))
main_page = MainPage()
main_page.main.show()
app.exec_()
