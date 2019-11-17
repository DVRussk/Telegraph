import random
import sys
import socket
import threading
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QFrame, QInputDialog
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
        self.hide_state = True
        self.hide()

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
        if len(self.messages) > 1 and self.messages[-2][0]['login'] == self.messages[-1][0]['login']:
            self.messages[-1][1].setText(message['text'])
        else:
            self.messages[-1][1].setText(message['login'] + ':\n' + message['text'])
        self.messages[-1][1].adjustSize()
        for i in self.messages[-2::-1]:
            i[1].move(self.x_pos * 1.05,
                      i[1].y() - self.messages[-1][1].height() - self.chat_height * 0.06)
        self.messages[-1][1].move(self.x_pos * 1.05,
                                  self.y_pos + self.chat_height - self.messages[-1][
                                      1].height() - self.chat_height * 0.03)
        if not self.hide_state:
            self.messages[-1][1].show()

    def hide(self):
        self.hide_state = True
        self.input.hide()
        self.btnIn.hide()
        for i in self.messages:
            i[1].hide()

    def show(self):
        self.hide_state = False
        self.input.show()
        self.btnIn.show()
        for i in self.messages:
            i[1].show()


class FirstForm(QMainWindow):
    progressChanged = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.create_chat_btn, self.invite_to_chat_btn = None, None
        self.Chats = {}
        self.Btns = {}
        self.initLog()
        self.current_chat = None

    def sendMes(self):
        if ''.join(self.Chats[self.current_chat].input.text().split()) == '':
            return
        self.sor.sendto(('0' + str(len(self.alias)) + self.alias + self.current_chat + str(random.randint(100000000,
                                                                                                          999999999)) +
                         self.Chats[
                             self.current_chat].input.text()).encode('utf-8'),
                        self.server)
        self.Chats[self.current_chat].input.clear()

    def initChat(self, chats):
        self.input_log.close()
        self.input_pas.close()
        self.btn_login.close()
        self.btn_logup.close()
        self.error_label.close()

        self.progressChanged.connect(self.receive_message)
        self.initChatUi(chats)

    def decode_message(self, raw_message):
        message_out = {}
        loglen = int(raw_message[1])
        message_out['login'] = raw_message[2:2 + loglen]
        message_out['chat_id'] = raw_message[2 + loglen:2 + loglen + 9]
        message_out['message_id'] = raw_message[2 + loglen + 9:2 + loglen + 9 + 9]
        message_out['text'] = raw_message[2 + loglen + 9 + 9:]
        return message_out

    def receive_message(self, raw_message):
        if raw_message[0] == '0':
            message = self.decode_message(raw_message)
            if message['chat_id'] in self.Chats:
                self.Chats[message['chat_id']].addMessage(message)
        elif raw_message[0] == '1':
            print(raw_message)
        elif raw_message[0] == '2':
            self.add_chat(raw_message[1:])

    def add_chat(self, num):
        print(num)
        width = QApplication.desktop().width()
        frame_width = (width / 2.5) / 3 * 4
        frame_height = (width / 2.5)
        self.Chats[num] = TextList(self.width() / 3, 0, self.width() / 3 * 2, self.height(), self)
        self.Btns[num] = QPushButton(num, self)
        self.Btns[num].resize(frame_width / 3, frame_height / 10)
        self.Btns[num].move(0, frame_height / 10 * (len(self.Chats) - 1))
        self.Btns[num].clicked.connect(self.choose_chat)
        self.Btns[num].show()

    def choose_chat(self):
        if self.current_chat is not None:
            self.Chats[self.current_chat].hide()
        self.current_chat = self.sender().text()
        self.Chats[self.current_chat].show()

    def invite(self):
        chat, ok = QInputDialog().getItem(self, "Inviting",
                                          "Chat", self.Chats, 0, False)
        if ok:
            login, ok = QInputDialog().getText(self, "Inviting", "Login")
            self.sor.sendto(('3' + str(len(self.alias)) + self.alias + str(chat) + login).encode('utf-8'),
                            self.server)

    def create(self):
        pass

    def initChatUi(self, chats):
        width = QApplication.desktop().width()
        frame_width = (width / 2.5) / 3 * 4
        frame_height = (width / 2.5)
        for j, i in enumerate(chats):
            self.Chats[i] = TextList(self.width() / 3, 0, self.width() / 3 * 2, self.height(), self)
            self.Btns[i] = QPushButton(i, self)
            self.Btns[i].resize(frame_width / 3, frame_height / 10)
            self.Btns[i].move(0, frame_height / 10 * j)
            self.Btns[i].clicked.connect(self.choose_chat)
            self.Btns[i].show()

        self.create_chat_btn = QPushButton('Create new chat', self)
        self.create_chat_btn.resize(frame_width / 6, frame_height / 10)
        self.create_chat_btn.move(0, frame_height * 0.9)
        self.create_chat_btn.clicked.connect(self.create)
        self.create_chat_btn.show()

        self.invite_to_chat_btn = QPushButton('Invite new member', self)
        self.invite_to_chat_btn.resize(frame_width / 6, frame_height / 10)
        self.invite_to_chat_btn.move(frame_width / 6, frame_height * 0.9)
        self.invite_to_chat_btn.clicked.connect(self.invite)
        self.invite_to_chat_btn.show()

        if self.current_chat in self.Chats:
            self.Chats[self.current_chat].show()

    def log_in(self):
        self.alias = self.input_log.text()
        print('1' + str(len(self.input_log.text())) + self.input_log.text() + str(
            len(self.input_pas.text())) + self.input_pas.text(), self.server)
        self.sor.sendto(
            ('1' + str(len(self.input_log.text())) + self.input_log.text() + str(
                len(self.input_pas.text())) + self.input_pas.text()).encode(
                'utf-8'),
            self.server)  # Уведомляем сервер о подключении

    def isLog(self, mes):
        if mes[0] == '2':
            self.progressChanged.disconnect(self.isLog)
            self.initChat(mes[1:].split(';'))
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

        self.server = '172.105.80.186', 9090  # Данные сервера
        self.sor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sor.bind(('', 0))  # Задаем сокет как клиент
        self.sor.connect(('172.105.80.186', 9090))

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
            print(data)
            self.progressChanged.emit(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstForm()

    sys.exit(app.exec())
