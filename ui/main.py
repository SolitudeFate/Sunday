import os
from threading import Thread

from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox
from qt_material import apply_stylesheet, QtStyleTools

from music_research import music_research
from ui.widget_slots.slots import add_all_items, find_data_song, find_test_song
from user_inquiry import answer_user_inquiry


class MainPage(QMainWindow, QtStyleTools):

    def __init__(self, api_key):
        super().__init__()
        self.main = QUiLoader().load('Index.ui')
        self.api_key = api_key

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
        self.main.button4.clicked.connect(self.answer_the_question)

        # 当用户在 QLineEdit 中输入文本并按下回车键时，returnPressed 信号会被触发，然后自动调用 QPushButton 的 click 方法，就像用户手动点击了按钮一样。
        # 将 QLineEdit 的 returnPressed 信号连接到按钮的 click 方法
        self.main.lineEdit_2.returnPressed.connect(self.main.button4.click)

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
    def open_music_player(self, song_path):
        os.startfile(song_path)

    # 开始识别
    def research_music(self):
        self.main.lineEdit.setText('')
        self.main.textEdit.setText('')
        index = self.main.comboBox1.currentIndex()
        if index != 0:
            test_song_name = self.main.comboBox1.currentText()
            test_song_path = find_test_song(test_song_name)
            thread1 = Thread(target=music_research, args=(self.api_key, test_song_path, self))
            thread2 = Thread(target=self.research_wait(), args=(self,))
            thread1.start()
            thread2.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要选择歌曲才能开始识别!')
            msg_box.exec_()

    # 播放识别后的歌曲
    def play_research_song(self):
        research_song_name = self.main.lineEdit.text()

        if research_song_name != '':
            research_song_path = find_data_song(research_song_name)
            if len(research_song_path) != 0:
                thread = Thread(target=self.open_music_player, args=(research_song_path,))
                thread.start()
            else:
                msg_box = QMessageBox(QMessageBox.Warning, '提示', '曲库中并没有这首歌！')
                msg_box.exec_()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要等待歌曲识别出结果后才能播放!')
            msg_box.exec_()

    # 识别等待
    def research_wait(self):
        msg_box = QMessageBox(QMessageBox.Warning, '提示', '接下来的识别过程需要您耐心地等待一段时间......')
        msg_box.exec_()

    # 回答问题
    def answer_the_question(self):
        self.main.textEdit.setText('')
        index = self.main.comboBox1.currentIndex()
        research_song_name = self.main.lineEdit.text()
        question = self.main.lineEdit_2.text()
        if index != 0 and research_song_name != '':
            thread = Thread(target=answer_user_inquiry, args=(self.api_key, research_song_name, question, self))
            thread.start()
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '你需要识别出歌曲以后才可以继续提问！')
            msg_box.exec_()

if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('Images/logo.png'))

    api_key = input("请输入你的chatglm的api_key：")

    main_page = MainPage(api_key)
    main_page.main.show()
    app.exec_()
