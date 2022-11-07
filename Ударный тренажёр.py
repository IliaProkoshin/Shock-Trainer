import sys  # Для удобства: длина программы без комментариев около 730 строк.
import sqlite3
from random import randint
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize

def pretty_view(text, bite):
    """
    Функция получает на вход текст на кириллице в нижнем регистре и число,
    обозначающее ударный слог. Возвращается слово с заглавной буквы и с
    выставленным в соответствии с числом ударением.
    """
    global letters, glasnie
    if bite == 1 and text[0] in glasnie:
        return f'{letters[text[0].upper()]}{text[1:]}'
    returner = text[0].upper()
    counter = 0
    if text[0] in glasnie:
        counter = 1
    for i in range(1, len(text)):
        if text[i] in glasnie:
            counter += 1
        if counter == bite:
            returner += letters[text[i]]
            if i != len(text) - 1:
                returner += text[i + 1:]
                break
        else:
            returner += text[i]
    return returner


def statist():
    """
    Функция считывает содержимое файла stat.txt, записывает статистику в
    соответствующие глобальные переменные.
    """
    global added, moves, true_moves, false_moves
    file = [int(x) for x in open('data/stat.txt', 'r').read().splitlines()]
    added = file[0]
    moves = file[1]
    true_moves = file[2]
    false_moves = file[3]


def writer():
    """
    Функция записывает статистику в файл stat.txt, используя данные из
    соответствующих глобальных переменных.
    """
    global added, moves, true_moves, false_moves
    file = open('data/stat.txt', 'w')
    file.write(f'{added}\n')
    file.write(f'{moves}\n')
    file.write(f'{true_moves}\n')
    file.write(f'{false_moves}')
    file.close()


letters = {'А': 'А́',  # Словарь для расстановки ударений
           'О': 'О́',
           'У': 'У́',
           'Ы': 'Ы́',
           'Э': 'Э́',
           'И': 'И́',
           'Е': 'Е́',
           'Ё': 'Ё',
           'Ю': 'Ю́',
           'Я': 'Я́',
           'а': 'а́',
           'о': 'о́',
           'у': 'у́',
           'ы': 'ы́',
           'э': 'э́',
           'и': 'и́',
           'е': 'е́',
           'ё': 'ё',
           'ю': 'ю́',
           'я': 'я́'
           }
glasnie = 'аоуыэиеёюя'  # Строка-ряд гласных букв русского языка


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация главного окна программы.
        """
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/MainWindow.ui', self)
        self.setFixedSize(1280, 768)
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(768, 1280))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.connected = sqlite3.connect('data/database.sqlite')
        self.cursor = self.connected.cursor()
        statist()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Слово', 'Часть речи', 'Длина',
                                              'Ударный слог',
                                              'Добавлено пользователем'])
        self.table.horizontalHeaderItem(0).setToolTip('Слово')
        self.table.horizontalHeaderItem(1).setToolTip('Часть речи')
        self.table.horizontalHeaderItem(
            2).setToolTip('Количество слогов в слове')
        self.table.horizontalHeaderItem(3).setToolTip(
            'Номер ударного слога')
        self.table.horizontalHeaderItem(
            4).setToolTip('Была ли эта запись добавлена пользователем')
        self.type_filter = [1, 2, 3, 4, 5, 6]
        self.added_filter = [True, False]
        self.sort_key = 'Default'
        self.sorting()
        self.Box1.stateChanged.connect(self.check_1)
        self.Box2.stateChanged.connect(self.check_2)
        self.Box3.stateChanged.connect(self.check_3)
        self.Box4.stateChanged.connect(self.check_4)
        self.Box5.stateChanged.connect(self.check_5)
        self.Box6.stateChanged.connect(self.check_6)
        self.Box7.stateChanged.connect(self.check_7)
        self.Box8.stateChanged.connect(self.check_8)
        self.Group.buttonClicked.connect(self.rad_but)
        self.ok_but.clicked.connect(self.start)
        self.redactor_but.clicked.connect(self.go_to_redactor)
        self.train_but.clicked.connect(self.go_to_trainer)
        self.stat_but.clicked.connect(self.go_to_statistics)
        self.ok_but.setStyleSheet('background: rgb(193,196,222);')
        self.redactor_but.setStyleSheet('background: rgb(193,196,222);')
        self.train_but.setStyleSheet('background: rgb(193,196,222);')
        self.stat_but.setStyleSheet('background: rgb(193,196,222);')

    def sorting(self):
        """
        Фильтрация и сортировка данных из базы данных, их отображение в
        виджете-таблице.
        """
        answer = []
        for t in self.type_filter:
            for ad in self.added_filter:
                result = self.cursor.execute(
                    """SELECT * FROM words WHERE type = ?
                    AND b_user_created = ?""",
                    (t, ad)).fetchall()
                for x in result:
                    if x not in answer:
                        answer.append(x)
        length = len(answer)
        self.table.setRowCount(0)
        self.table.setRowCount(length)
        if self.sort_key == 'Default':
            answer.sort(key=lambda x: x[0])
        elif self.sort_key == 'Length':
            answer.sort(key=lambda x: x[3])
        elif self.sort_key == 'Alph':
            answer.sort(key=lambda x: x[1])
        elif self.sort_key == 'Type':
            answer.sort(key=lambda x: x[2])
        counter = 0
        for one in answer:
            text = pretty_view(str(one[1]), one[4])
            self.table.setItem(
                counter, 0, QTableWidgetItem(text))
            text = one[2]
            if text == 1:
                text = 'существительное'
            elif text == 2:
                text = 'прилагательное'
            elif text == 3:
                text = 'глагол'
            elif text == 4:
                text = 'причастие/отглагольное прилагательное'
            elif text == 5:
                text = 'деепричастие'
            elif text == 6:
                text = 'наречие'
            added = QTableWidgetItem(text)
            added.setTextAlignment(
                Qt.AlignVCenter | Qt.AlignHCenter)
            self.table.setItem(
                counter, 1, added)
            added = QTableWidgetItem(str(one[3]))
            added.setTextAlignment(
                Qt.AlignVCenter | Qt.AlignHCenter)
            self.table.setItem(
                counter, 2, QTableWidgetItem(added))
            added = QTableWidgetItem(str(one[4]))
            added.setTextAlignment(
                Qt.AlignVCenter | Qt.AlignHCenter)
            self.table.setItem(
                counter, 3, QTableWidgetItem(added))
            if one[5]:
                text = QTableWidgetItem('Да')
            else:
                text = QTableWidgetItem('Нет')
            text.setTextAlignment(
                Qt.AlignCenter | Qt.AlignCenter)
            self.table.setItem(
                counter, 4, text)
            counter += 1
        self.table.resizeColumnsToContents()
        self.number(len(answer))

    def check_1(self, state):
        """
        Обработка взаимодействий с Box1.
        """
        if state == Qt.Checked:
            self.type_filter.append(1)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 1:
                    del self.type_filter[i]
                    return

    def check_2(self, state):
        """
        Обработка взаимодействий с Box2.
        """
        if state == Qt.Checked:
            self.type_filter.append(2)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 2:
                    del self.type_filter[i]
                    return

    def check_3(self, state):
        """
        Обработка взаимодействий с Box3.
        """
        if state == Qt.Checked:
            self.type_filter.append(3)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 3:
                    del self.type_filter[i]
                    return

    def check_4(self, state):
        """
        Обработка взаимодействий с Box4.
        """
        if state == Qt.Checked:
            self.type_filter.append(4)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 4:
                    del self.type_filter[i]
                    return

    def check_5(self, state):
        """
        Обработка взаимодействий с Box5.
        """
        if state == Qt.Checked:
            self.type_filter.append(5)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 5:
                    del self.type_filter[i]
                    return

    def check_6(self, state):
        """
        Обработка взаимодействий с Box6.
        """
        if state == Qt.Checked:
            self.type_filter.append(6)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 6:
                    del self.type_filter[i]
                    return

    def check_7(self, state):
        """
        Обработка взаимодействий с Box7.
        """        
        if state == Qt.Checked:
            self.added_filter.append(True)
        else:
            for i in range(len(self.added_filter)):
                if self.added_filter[i] == True:
                    del self.added_filter[i]
                    return

    def check_8(self, state):
        """
        Обработка взаимодействий с Box8.
        """
        if state == Qt.Checked:
            self.added_filter.append(False)
        else:
            for i in range(len(self.added_filter)):
                if self.added_filter[i] == False:
                    del self.added_filter[i]
                    return

    def rad_but(self):
        """
        Обработка взаимодействий с группой радиокнопок.
        """
        if self.radio1.isChecked():
            self.sort_key = 'Default'
        elif self.radio2.isChecked():
            self.sort_key = 'Length'
        elif self.radio3.isChecked():
            self.sort_key = 'Type'
        else:
            self.sort_key = 'Alph'

    def start(self):
        """
        Обработка нажатий на кнопку Применить.
        """
        self.sorting()
        
    def number(self, number):
        """
        Функция возвращает слово "слова" в нужной форме, согласуя его с
        поступившим на вход числом.
        """
        if number == 0:
            self.label_info.setText('Ничего не найдено')
            return
        if number >= 1 and number <= 9:
            if number == 1:
                text = 'слово'
            elif number >= 2 and number <= 4:
                text = 'слова'
            else:
                text = 'слов'
        elif int(str(number)[-2:]) in [11, 12, 13, 14, 15, 16, 17, 18, 19]:
            text = 'слов'
        elif number % 10 == 0:
            text = 'слов'
        elif number % 10 == 1:
            text = 'слово'
        elif number % 10 in [2, 3, 4]:
            text = 'слова'
        else:
            text = 'слов'
        self.label_info.setText(f'Отображено {number} {text}')

    def go_to_redactor(self):
        """
        Переход в окно Редактора по нажатию кнопки Редактировать.
        """
        global ex
        ex.close()
        ex = RedactorWindow()
        ex.show()

    def go_to_trainer(self):
        """
        Переход в окно Тренажёра по нажатию кнопки Тренужёр.
        """
        global ex
        ex.close()
        ex = TrainerWindow()
        ex.show()

    def go_to_statistics(self):
        """
        Переход в окно Статистики по нажатию кнопки Статистика.
        """
        global ex
        ex.close()
        ex = StatWindow()
        ex.show()

    def closeEvent(self, event):
        """
        Вызов функции writer при закрытии окна.
        """
        writer()
        event.accept()

class StartWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация стартового информационного окна программы.
        """
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/StartWindow.ui', self)
        self.setFixedSize(450, 250)
        self.continue_but.clicked.connect(self.go_to_main)
        self.continue_but.setStyleSheet('background: rgb(127,255,212);')
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(450, 250))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)

    def go_to_main(self):
        """
        Переход на основное окно по нажатию кнопки Вперёд!
        """
        global ex
        ex.close()
        ex = MainWindow()
        ex.show()

class RedactorWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация окна Редактора.
        """
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/RedactorWindow.ui', self)
        self.setFixedSize(600, 400)
        statist()
        self.return_but.clicked.connect(self.go_to_main)
        self.return_but.setStyleSheet('background: rgb(193,196,222);')
        self.add_but.setStyleSheet('background: rgb(193,196,222);')
        self.del_but.setStyleSheet('background: rgb(193,196,222);')
        self.ok_but.setStyleSheet('background: rgb(127,255,212);')
        self.cancel_but.setStyleSheet('background: rgb(240,128,128);')
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(600, 400))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.hider()
        self.connected = sqlite3.connect('data/database.sqlite')
        self.cursor = self.connected.cursor()
        self.del_but.clicked.connect(self.deleting)
        self.cancel_but.clicked.connect(self.hider)
        self.add_but.clicked.connect(self.adding)
        self.ok_but.clicked.connect(self.redact)
        self.reg_del = 'Режим удаления (только пользовательские слова)'
        self.reg_add = 'Режим добавления'
        self.do_switch = 0

    def go_to_main(self):
        """
        Переход на основное окно по нажатию кнопки На главную.
        """
        global ex
        ex.close()
        ex = MainWindow()
        ex.show()

    def deleting(self):
        """
        Переход в режим удаления.
        """
        self.hider()
        self.information_lab.setText(self.reg_del)
        self.word.show()
        self.label_word.show()
        self.ok_but.show()
        self.cancel_but.show()
        self.do_switch = 2

    def hider(self):
        """
        Скрытие всех элементов интерфейса, т.е. переход в изначальный режим
        программы.
        """
        self.do_switch = 0
        self.information_lab.setText('')
        self.word.setText('')
        self.word.hide()
        self.label_word.hide()
        self.label_strike.hide()
        self.label_wtype.hide()
        self.type_info.hide()
        self.strike.setValue(1)
        self.wtype.setValue(1)
        self.strike.hide()
        self.wtype.hide()
        self.ok_but.hide()
        self.cancel_but.hide()

    def adding(self):
        """
        Переход в режим добавления.
        """
        self.hider()
        self.information_lab.setText(self.reg_add)
        self.ok_but.show()
        self.cancel_but.show()
        self.label_word.show()
        self.label_strike.show()
        self.label_wtype.show()
        self.type_info.show()
        self.word.show()
        self.strike.show()
        self.wtype.show()
        self.do_switch = 1

    def redact(self):
        """
        Обработка внесённых изменений по нажатию кнопки Применить.
        """
        global glasnie, added
        text = self.word.text().lower()
        if len(text) == 0:
            self.dialog('Введите слово!')
            return
        alph = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        for let in text:
            if let not in alph:
                self.dialog('Ошибка в слове!')
                return
        if self.do_switch == 1:
            result = self.cursor.execute(
                """SELECT name FROM words""").fetchall()
            for x in result:
                if x[0] == text:
                    self.dialog('Слово уже записано!')
                    return
            counter = 0
            for x in text:
                if x in glasnie:
                    counter += 1
            strike = self.strike.value()
            if strike > counter:
                self.dialog('Ошибка ударения!')
                return
            self.cursor.execute("""INSERT INTO words (name, type, length,
            strike,b_user_created)
            VALUES (?, ?, ?, ?, 1)""", (text, self.wtype.value(), counter,
                                        strike))
            self.connected.commit()
            added += 1
            self.dialog('Успешно добавлено!')
        elif self.do_switch == 2:
            result = self.cursor.execute(
                """SELECT * FROM words WHERE name = ?""", (text,)).fetchall()
            if len(result) == 0:
                self.dialog('Нет слова в базе!')
                return
            if len(result) > 1:
                self.dialog('Избыток совпадений!')
                return
            if not result[0][5]:
                self.dialog('Запрещено удалять!')
                return
            self.cursor.execute("""DELETE from words where ID = ?""",
                                (result[0][0],))
            self.connected.commit()
            added -= 1
            self.dialog('Успешно удалено!')
        self.strike.setValue(1)
        self.wtype.setValue(1)
        self.word.setText('')

    def dialog(self, text):
        """
        Отображение диалогового окна при нажатии кнопки Применить. В диалоговом
        окне отображается результат редактирования - успешный или нет.
        """
        self.sub_window = Dialog(text)
        self.sub_window.show()

    def closeEvent(self, event):
        """
        Вызов функции writer при закрытии окна.
        """
        writer()
        event.accept()    


class Dialog(QMainWindow):
    def __init__(self, text):
        """
        Инициализация диалогового окна.
        """
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/Dialog.ui', self)
        self.setFixedSize(300, 150)
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(300, 150))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.info.setText(text)
        self.close_but.clicked.connect(self.closing)

    def closing(self):
        """
        Закрытие диалогового окна по нажатию кнопки OK.
        """
        global ex
        ex.sub_window.close()


class TrainerWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация окна Тренажёра.
        """
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/TrainerWindow.ui', self)
        statist()
        self.setFixedSize(600, 400)
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(600, 400))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.Box1.stateChanged.connect(self.check_1)
        self.Box2.stateChanged.connect(self.check_2)
        self.Box3.stateChanged.connect(self.check_3)
        self.Box4.stateChanged.connect(self.check_4)
        self.Box5.stateChanged.connect(self.check_5)
        self.Box6.stateChanged.connect(self.check_6)
        self.Box7.stateChanged.connect(self.check_7)
        self.Box8.stateChanged.connect(self.check_8)
        self.Box9.stateChanged.connect(self.check_9)
        self.type_filter = [1, 2, 3, 4, 5, 6]
        self.added_filter = [True, False]
        self.only_one = 0
        self.return_but.clicked.connect(self.go_to_main)
        self.return_but.setStyleSheet('background: rgb(193,196,222);')
        self.start_but.setStyleSheet('background: rgb(193,196,222);')
        self.start_but.clicked.connect(self.start_game)
        self.connected = sqlite3.connect('data/database.sqlite')
        self.cursor = self.connected.cursor()
        self.break_but.hide()
        self.answer_but.hide()
        self.info_panel.hide()
        self.break_but.setStyleSheet('background: rgb(193,196,222);')
        self.answer_but.setStyleSheet('background: rgb(193,196,222);')
        self.closed1.hide()
        self.closed2.hide()
        self.answer_box.hide()
        self.break_but.clicked.connect(self.stop)
        self.answer_but.clicked.connect(self.take_answer)

    def check_1(self, state):
        """
        Обработка взаимодействий с Box1.
        """
        if state == Qt.Checked:
            self.type_filter.append(1)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 1:
                    del self.type_filter[i]
                    return

    def check_2(self, state):
        """
        Обработка взаимодействий с Box2.
        """
        if state == Qt.Checked:
            self.type_filter.append(2)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 2:
                    del self.type_filter[i]
                    return

    def check_3(self, state):
        """
        Обработка взаимодействий с Box3.
        """
        if state == Qt.Checked:
            self.type_filter.append(3)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 3:
                    del self.type_filter[i]
                    return

    def check_4(self, state):
        """
        Обработка взаимодействий с Box4.
        """
        if state == Qt.Checked:
            self.type_filter.append(4)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 4:
                    del self.type_filter[i]
                    return

    def check_5(self, state):
        """
        Обработка взаимодействий с Box5.
        """
        if state == Qt.Checked:
            self.type_filter.append(5)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 5:
                    del self.type_filter[i]
                    return

    def check_6(self, state):
        """
        Обработка взаимодействий с Box6.
        """
        if state == Qt.Checked:
            self.type_filter.append(6)
        else:
            for i in range(len(self.type_filter)):
                if self.type_filter[i] == 6:
                    del self.type_filter[i]
                    return

    def check_7(self, state):
        """
        Обработка взаимодействий с Box7.
        """
        if state == Qt.Checked:
            self.added_filter.append(True)
        else:
            for i in range(len(self.added_filter)):
                if self.added_filter[i] == True:
                    del self.added_filter[i]
                    return

    def check_8(self, state):
        """
        Обработка взаимодействий с Box8.
        """
        if state == Qt.Checked:
            self.added_filter.append(False)
        else:
            for i in range(len(self.added_filter)):
                if self.added_filter[i] == False:
                    del self.added_filter[i]
                    return

    def check_9(self, state):
        """
        Обработка взаимодействий с Box9.
        """
        if state == Qt.Checked:
            self.only_one = 1
        else:
            self.only_one = 0

    def go_to_main(self):
        """
        Переход на основное окно по нажатию кнопки На главную.
        """
        global ex
        ex.close()
        ex = MainWindow()
        ex.show()

    def start_game(self):
        """
        Обработка начала игры, отображения первого вопроса и нужных элементов
        интерфейса.
        """
        global glasnie
        self.info_panel.setText('Ходов 0, правильно 0, неправильно 0.')
        self.answer_box.setValue(1)
        self.answer = []
        for t in self.type_filter:
            for ad in self.added_filter:
                result = self.cursor.execute(
                    """SELECT * FROM words WHERE type = ?
                    AND b_user_created = ?""",
                    (t, ad)).fetchall()
                for x in result:
                    if x not in self.answer:
                        self.answer.append(x)
        if len(self.answer) == 0:
            self.dialog('Пустой набор слов!')
            return
        self.length = self.number.value()
        if self.only_one:
            if len(self.answer) < self.length:
                self.dialog('Недостаточно слов!')
                self.info_panel.hide()
                return
        self.answer_box.show()
        self.info_panel.show()
        self.counter = 0
        self.true_answer = 0
        self.false_answer = 0
        self.start_but.setEnabled(False)
        self.closed1.show()
        self.closed2.show()
        self.break_but.show()
        self.answer_but.show()
        now_num = randint(0, len(self.answer) - 1)
        self.word = self.answer[now_num]
        self.quest.setText(
            f'На какой слог падает ударение в слове {self.word[1]}?')
        if self.only_one:
            del self.answer[now_num]
        self.answer_box.setMaximum(self.word[3])


    def dialog(self, text):
        """
        Открытие диалогового окна при запуске игры с нулевой выборкой базы
        данных.
        """
        self.sub_window = Dialog(text)
        self.sub_window.show()

    def stop(self):
        """
        Обработка нажатия на кнопку Стоп.
        """
        self.start_but.setEnabled(True)
        self.closed1.hide()
        self.closed2.hide()
        self.break_but.hide()
        self.answer_but.hide()
        self.info_panel.setText('')
        self.returner_panel.setText('')
        self.quest.setText('')
        self.answer_box.hide()

    def take_answer(self):
        """
        Обработка нажатия на кнопку Ответить, отображение результата, вывод
        следующего вопроса либо результатов игры в диалоговом окне.
        """
        global moves, true_moves, false_moves
        self.counter += 1
        moves += 1
        if self.answer_box.value() == self.word[4]:
            self.true_answer += 1
            self.returner_panel.setText('Правильно!')
            true_moves += 1
        else:
            self.false_answer += 1
            self.returner_panel.setText(
                f'Ошибка. Правильно - {self.word[4]}')
            false_moves += 1
        text = (f'Ходов {self.counter}, правильно {self.true_answer}, ' +
                f'неправильно {self.false_answer}.')
        self.info_panel.setText(text)
        if self.counter == self.length:
            self.stop()
            text = (f'{self.true_answer} правильных, ' +
            f'{self.false_answer} неправильных.')
            self.dialog(text)
            return
        now_num = randint(0, len(self.answer) - 1)
        self.word = self.answer[now_num]
        self.quest.setText(
            f'На какой слог падает ударение в слове {self.word[1]}?')
        if self.only_one:
            del self.answer[now_num]
        self.answer_box.setMaximum(self.word[3])
        self.answer_box.setValue(1)

    def closeEvent(self, event):
        """
        Вызов функции writer при закрытии окна.
        """
        writer()
        event.accept()    


class StatWindow(QMainWindow):
    def __init__(self):
        """
        Инициализация окна Статистики.
        """
        global added, moves, true_moves, false_moves
        super().__init__()
        self.setWindowIcon(QIcon('graphic/logo.png'))
        uic.loadUi('UI/StatWindow.ui', self)
        self.setFixedSize(400, 270)
        background = QImage('graphic/background.jpg')
        background_scaled = background.scaled(QSize(400, 270))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_scaled))
        self.setPalette(palette)
        self.but.setStyleSheet('background: rgb(193,196,222);')
        self.but.clicked.connect(self.go_to_main)
        self.list.addItem(f'Слов добавлено в базу: {added};')
        self.list.addItem(f'Ходов в тренажёре: {moves};')
        self.list.addItem(f'Правильных ответов в тренажёре: {true_moves};')
        self.list.addItem(f'Ошибок в тренажёре: {false_moves}.')
        self.but_2.setStyleSheet('background: rgb(240,128,128);')
        self.but_2.clicked.connect(self.clear)

    def go_to_main(self):
        """
        Переход на основное окно по нажатию кнопки На главную.
        """
        global ex
        ex.close()
        ex = MainWindow()
        ex.show()

    def clear(self):
        """
        Очистка статистики и её перезапись по нажатию кнопки Сброс.
        """
        global added, moves, true_moves, false_moves
        moves = 0
        true_moves = 0
        false_moves = 0
        self.list.clear()
        self.list.addItem(f'Слов добавлено в базу: {added};')
        self.list.addItem(f'Ходов в тренажёре: {moves};')
        self.list.addItem(f'Правильных ответов в тренажёре: {true_moves};')
        self.list.addItem(f'Ошибок в тренажёре: {false_moves}.')
        self.but_2.setStyleSheet('background: rgb(240,128,128);')
        self.but_2.clicked.connect(self.clear)
        writer()


def except_hook(cls, exception, traceback):
    """
    Обработка возникающих исключений, консольный вывод ошибок.
    """
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    """
    Запуск программы.
    """
    file = [int(x) for x in open('data/stat.txt', 'r').read().splitlines()]
    added = file[0]
    moves = file[1]
    true_moves = file[2]
    false_moves = file[3]
    app = QApplication(sys.argv)
    ex = StartWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
