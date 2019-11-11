import queue
import sys
import socket
import threading
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QFrame
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtWidgets import QLCDNumber, QLineEdit
from PyQt5 import QtCore, QtGui, QtWidgets


class TextList(QWidget):
    def __init__(self, x_pos, y_pos, width, height, form):
        super().__init__(parent=form)
        self.newMessages = list()
        self.form = form
        self.full_height = height
        self.x_pos, self.y_pos, self.width, self.chat_height = x_pos, y_pos, width, height * 0.9
        self.messages = list()
        self.inputUi()

    def inputUi(self):
        self.input = QLineEdit(self.form)
        self.input.resize(100, 50)
        self.input.resize(self.width * 0.79, self.full_height * 0.09)
        self.input.move(self.x_pos + self.width * 0.005, self.y_pos + self.chat_height + self.full_height * 0.005)

        self.btnIn = QPushButton('Send', self.form)
        self.btnIn.resize(self.width * 0.20, self.full_height * 0.09)
        self.btnIn.move(self.x_pos + self.width * 0.01 + self.width * 0.79,
                        self.y_pos + self.chat_height + self.full_height * 0.005)
        self.btnIn.clicked.connect(self.form.sendMes)
        self.input.show()
        self.btnIn.show()

    def addMessage(self, message):
        self.messages.append((message, QLabel(self.form)))
        self.messages[-1][1].setWordWrap(True)
        self.messages[-1][1].setMaximumWidth(self.width * 0.9)
        if len(self.messages) > 1 and self.messages[-2][0][0] == self.messages[-1][0][0]:
            self.messages[-1][1].setText(message[1])
        else:
            self.messages[-1][1].setText(message[0] + ':\n' + message[1])
        self.messages[-1][1].adjustSize()
        for i in self.messages[-2::-1]:
            i[1].move(self.x_pos * 1.05,
                      i[1].y() - self.messages[-1][1].height() - self.chat_height * 0.06)
        self.messages[-1][1].move(self.x_pos * 1.05,
                                  self.y_pos + self.chat_height - self.messages[-1][
                                      1].height() - self.chat_height * 0.03)
        self.messages[-1][1].show()


class FirstForm(QMainWindow):
    progressChanged = QtCore.pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.initLog()

    def sendMes(self):
        if ''.join(self.Chat.input.text().split()) == '':
            return
        self.sor.sendto(('0' + str(len(self.alias)) + self.alias + self.Chat.input.text()).encode('utf-8'),
                        self.server)
        self.Chat.input.clear()

    def initChat(self):
        self.input_log.close()
        self.input_pas.close()
        self.btn_login.close()
        self.btn_logup.close()
        self.error_label.close()

        self.initChatUi()
        self.progressChanged.connect(self.Chat.addMessage)

    def initChatUi(self):
        self.Chat = TextList(self.width() / 3, 0, self.width() / 3 * 2, self.height(), self)

    def log_in(self):
        self.alias = self.input_log.text()
        self.sor.sendto(
            ('1' + str(len(self.input_log.text())) + self.input_log.text() + str(
                len(self.input_pas.text())) + self.input_pas.text()).encode(
                'utf-8'),
            self.server)  # Уведомляем сервер о подключении

    def isLog(self, mes):
        if 'connected to server' in mes[1]:
            self.initChat()
            self.Chat.addMessage(mes)
            self.progressChanged.disconnect(self.isLog)
        else:
            self.error_label.setText(mes[0] + ': ' + mes[1])
            print('Error')

    def initLog(self):
        width = QApplication.desktop().width()
        frame_width = (width / 2.5) / 3 * 4
        frame_height = (width / 2.5)
        self.setGeometry(0, 0, (width / 2.5) / 3 * 4, (width / 2.5))
        self.setWindowTitle('ТелеграфЪ')

        self.error_label = QLabel(self)
        self.error_label.resize(frame_width / 3, frame_height / 12)
        self.error_label.move(frame_width / 2 - (frame_width / 8), frame_height * 0.50)
        self.error_label.setWordWrap(True)

        self.btn_login = QPushButton('Log In', self)
        self.btn_login.resize(frame_width / 2.5, frame_height / 10)
        self.btn_login.move(frame_width / 2 - (frame_width / 5), frame_height * 0.60)

        self.btn_logup = QPushButton('Log Up', self)
        self.btn_logup.resize(frame_width / 4, frame_height / 14)
        self.btn_logup.move(frame_width / 2 - (frame_width / 8), frame_height * 0.73)

        self.input_log = QLineEdit(self)
        self.input_log.resize(frame_width / 2, frame_height / 15)
        self.input_log.move(frame_width / 2 - (frame_width / 4), frame_height * 0.35)

        self.input_pas = QLineEdit(self)
        self.input_pas.resize(frame_width / 2, frame_height / 15)
        self.input_pas.move(frame_width / 2 - (frame_width / 4), frame_height * 0.45)

        self.server = 'localhost', 9090  # Данные сервера
        self.sor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sor.bind(('', 0))  # Задаем сокет как клиент
        self.sor.connect(('localhost', 9090))

        self.thread1 = threading.Thread(target=self.read_sok)
        self.thread1.start()
        self.progressChanged.connect(self.isLog)
        self.btn_login.clicked.connect(self.log_in)
        self.btn_logup.clicked.connect(self.log_up)

        self.coords = QLabel(self)
        self.coords.setText("a " * 10000)
        self.coords.move(self.width() / 3, 0)
        self.coords.resize(self.width() / 3 * 2, self.height() * 0.9)
        self.coords.setWordWrap(True)
        self.coords.close()
        self.show()

    def log_up(self):
        self.alias = self.input_log
        self.sor.sendto(
            ('2' + str(len(self.input_log.text())) + self.input_log.text() + str(
                len(self.input_pas.text())) + self.input_pas.text()).encode(
                'utf-8'),
            self.server)  # Уведомляем сервер о подключении

    def mouseMoveEvent(self, event):
        pass
        # print(self.coords.sizeHint())
        # self.coords.setText('f ' * event.x())
        # self.coords.resize(100, self.coords.sizeHint().height())

    def read_sok(self):
        while 1:
            data = self.sor.recv(1024).decode('utf-8')
            loglen = int(data[0])
            data.find(' ')
            print(data)
            self.progressChanged.emit((data[1:1 + loglen], data[1 + loglen:]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstForm()

    sys.exit(app.exec())
