import sys
import os
import pyperclip
import requests
import webbrowser
from threading import Thread
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QDesktopWidget, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtGui import *
from telethon import TelegramClient
import asyncio
import pickle
from session_creator import *
from id_manager import *

version = 'v1.2'
new_version = ''


def version_check():  # for checking new releases on github
    global new_version
    response = requests.get(
        "https://api.github.com/repos/Sakib0194/Telecounter/releases/latest")
    new_version = response.json()["name"]


Thread(target=version_check).start()

api_id = 1234567
api_hash = 'test'
client = ''

if os.path.exists('resource/kpi_id.pckl'):
    pass
else:
    data_store = open('kpi_id.pckl', 'wb')
    pickle.dump({}, data_store)
    data_store.close()

data_store = open('resource/kpi_id.pckl', 'rb')  # retrieve saved kpi id
accounts = pickle.load(data_store)
data_store.close()


class version_form(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowIcon(QIcon('resource/logo.png'))
        except Exception:
            pass
        layout = QVBoxLayout()
        layout_2 = QHBoxLayout()
        self.label = QLabel(f'New Version {new_version} is available')
        layout.addWidget(self.label)
        self.button_update = QPushButton('Update')
        self.button_cancel = QPushButton('Cancel')
        layout_2.addWidget(self.button_update)
        layout_2.addWidget(self.button_cancel)
        layout.addLayout(layout_2)
        self.setLayout(layout)
        self.button_update.clicked.connect(self.update_gui)
        self.button_cancel.clicked.connect(self.exiting)

    def update_gui(self):
        webbrowser.open_new(
            'https://github.com/Sakib0194/Telecounter/releases')

    def exiting(self):
        self.close()


class main_form(QMainWindow):
    global client

    def __init__(self):
        super().__init__()
        try:
            self.setWindowIcon(QIcon('resource/logo.png'))
        except Exception:
            pass
        self.ui = uic.loadUi('resource/Design.ui', self)
        self.group_name = ''
        self.group_name_2 = ''
        self.group_starting = 0
        self.group_ending = 0
        self.cu_session = ''
        self.running = False
        self.force_stop = 3
        self.counting_time = 3
        self.cu_dots = ''
        self.create_log = True
        self.reload_pressed = False
        self.starting_paste = True
        self.ending_paste = True
        self.total_row_all = 0
        self.kpi_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.all_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.kpi_cells = {}
        self.all_cells = {}
        self.total_mess_char = {}
        self.largest_text_all = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.largest_text_kpi = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.largest_string_all = {0: '', 1: '', 2: '', 3: '', 4: ''}
        self.largest_string_kpi = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.cu_selected_all = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.cu_selected_kpi = {0: [], 1: [], 2: [], 3: [], 4: []}

        self.manager = id_manager(self.ui)
        self.sess = session_builder(self.ui)
        self.session_detector()
        self.exit_detector()
        self.connections()
        self.modifier()
        self.timer = QTimer()
        # run the function after 10 seconds
        self.timer.timeout.connect(self.check_update)
        self.timer.setInterval(10000)
        self.timer.start()
        self.show()

        # self.check_update()

    def connections(self):  # connect all events
        self.ui.button_create_sess.clicked.connect(self.sess.sess_creator)
        self.ui.button_send_code.clicked.connect(self.sess.tg_code_sender)
        self.ui.button_clear_1.clicked.connect(self.edit_box_1)
        self.ui.button_clear_2.clicked.connect(self.edit_box_2)
        self.ui.button_reload.clicked.connect(self.reload_router)
        self.ui.button_add_user.clicked.connect(self.manager.add_user)
        self.ui.listWidget.itemClicked.connect(self.manager.list_selected)
        self.ui.button_remove.clicked.connect(self.manager.list_remove)
        self.ui.button_save.clicked.connect(self.manager.list_save)
        self.ui.box_ending_mess.textChanged.connect(self.text_changed_ending)
        self.ui.box_starting_mess.textChanged.connect(self.text_changed_starting)
        self.ui.table_widget_1.selectionModel().selectionChanged.connect(self.selected_rows_1)
        self.ui.table_widget_2.selectionModel().selectionChanged.connect(self.selected_rows_2)
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.ui.Button_count.clicked.connect(self.data_parser)
        self.ui.button_exit.clicked.connect(self.exiting)
        self.ui.table_widget_1.horizontalHeader().sortIndicatorChanged.connect(self.sorting_event_1)
        self.ui.table_widget_2.horizontalHeader().sortIndicatorChanged.connect(self.sorting_event_2)

    def modifier(self):  # modify widgets, button before the window loads
        self.ui.button_save.setEnabled(False)
        self.ui.button_remove.setEnabled(False)
        self.ui.button_add_user.setEnabled(False)
        self.ui.button_clear_2.setText('Paste')
        self.ui.button_clear_1.setText('Paste')
        self.resize(400, 350)
        self.ui.box_tg_code.resize(75, 30)
        self.ui.button_send_code.resize(90, 30)
        self.ui.table_widget_1.setColumnWidth(0, 115)
        self.ui.table_widget_2.setColumnWidth(0, 115)
        self.ui.table_widget_1.setColumnWidth(1, 110)
        self.ui.table_widget_2.setColumnWidth(1, 110)
        self.ui.table_widget_1.setColumnWidth(2, 80)
        self.ui.table_widget_2.setColumnWidth(2, 80)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def check_update(self):  # for opening the new version available form
        print('Current Version', version)
        if version != new_version:
            self.w = version_form()
            self.w.show()
        self.timer.stop()

    def sorting_event_1(self):
        self.all_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.cu_selected_all = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.largest_string_all = {0: '', 1: '', 2: '', 3: '', 4: ''}
        self.largest_text_all = {0: 0, 1: 0, 2: 0, 3: 0, 3: 0}
        self.all_cells = {}

        # forget all previous saved data, clear selection on sorting

        self.ui.table_widget_1.clearSelection()
        for column in range(5):
            for row in range(self.total_row_all):
                try:
                    cu_value = str(
                        self.ui.table_widget_1.item(row, column).text())
                    self.all_log[column].append(cu_value)
                except Exception:
                    pass

    def sorting_event_2(self):
        self.kpi_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.cu_selected_kpi = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.largest_string_kpi = {0: '', 1: '', 2: '', 3: '', 4: ''}
        self.largest_text_kpi = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        self.kpi_cells = {}

        # forget all previous saved data, clear selection on sorting

        self.ui.table_widget_2.clearSelection()
        for column in range(5):
            for row in range(self.total_row_all):
                try:
                    cu_value = str(
                        self.ui.table_widget_2.item(row, column).text())
                    self.kpi_log[column].append(cu_value)
                except Exception:
                    pass

    def keyPressEvent(self, event):
        if QKeySequence(event.key()+int(event.modifiers())) == QKeySequence("Ctrl+C"):

            # sort selected cells by row and column on both tables
            self.all_cells = dict(sorted(self.all_cells.items()))
            for i in self.all_cells:
                self.all_cells[i] = dict(sorted(self.all_cells[i].items()))

            self.kpi_cells = dict(sorted(self.kpi_cells.items()))
            for i in self.kpi_cells:
                self.kpi_cells[i] = dict(sorted(self.kpi_cells[i].items()))

            full_text = ''
            line_added = False

            # go through all selected cells
            # and add spaces to keep the lines aligned on copy/ctrl + c
            # amount of spaces is determined by the largest text selected
            # on that specific column

            for i in self.all_cells:
                if self.all_cells[i] != {}:
                    try:
                        for a in self.all_cells[i]:
                            if self.all_cells[i][a] != []:
                                for x in self.all_cells[i][a]:
                                    full_text += f'{x}'.ljust(self.largest_text_all[a])
                                    line_added = True
                            else:
                                line_added = False
                        if line_added is True:
                            full_text += '\n'
                    except Exception as e:
                        print(e)

            line_added = False
            for i in self.kpi_cells:
                if self.kpi_cells[i] != {}:
                    try:
                        for a in self.kpi_cells[i]:
                            if self.kpi_cells[i][a] != []:
                                for x in self.kpi_cells[i][a]:
                                    if x is not None:
                                        full_text += f'{x}'.ljust(self.largest_text_kpi[a])
                                        line_added = True
                                    else:
                                        line_added = False
                            else:
                                line_added = False
                        if line_added is True:
                            full_text += '\n'
                    except Exception as e:
                        print(e)

            pyperclip.copy(full_text)
            self.ui.statusBar().showMessage(f'Cells Copied')

    def tab_changed(self):  # resize form if message log tab selected
        if self.ui.tabWidget.currentIndex() == 1:
            self.resize(850, 400)
        else:
            self.resize(400, 350)

    def selected_rows_1(self, selected, deselected):
        # save row number, column number and the cell text on select
        for i in selected.indexes():
            try:
                if int(i.row()) in self.all_cells:
                    if int(i.column()) not in self.all_cells[int(i.row())]:
                        self.all_cells[int(i.row())][int(i.column())] = []
                    self.all_cells[int(i.row())][int(i.column())].append(
                        self.all_log[int(i.column())][int(i.row())])
                elif int(i.row()) not in self.all_cells:
                    self.all_cells[int(i.row())] = {}
                    if int(i.column()) not in self.all_cells[int(i.row())]:
                        self.all_cells[int(i.row())][int(i.column())] = []
                    self.all_cells[int(i.row())][int(i.column())].append(
                        self.all_log[int(i.column())][int(i.row())])

                # keep the largest text length in check for every selection

                cu_value = str(self.ui.table_widget_1.item(
                    i.row(), i.column()).text())
                self.cu_selected_all[i.column()].append(cu_value)
                if len(cu_value) >= self.largest_text_all[int(i.column())]:
                    self.largest_text_all[int(i.column())] = len(cu_value) + 1
                    self.largest_string_all[i.column()] = cu_value

            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        for i in deselected.indexes():
            try:
                if self.all_cells == {}:
                    pass
                else:

                    # remove from saved selected cells and check whether
                    # the largest text length changed

                    try:
                        del self.all_cells[int(i.row())][int(i.column())]
                    except Exception:
                        self.all_cells = {}

                    cu_value = str(self.ui.table_widget_1.item(
                        i.row(), i.column()).text())
                    try:
                        self.cu_selected_all[int(i.column())].remove(cu_value)
                    except Exception:
                        self.cu_selected_all = {
                            0: [], 1: [], 2: [], 3: [], 4: []}

                    self.largest_string_all[i.column()] = ''
                    self.largest_text_all[int(i.column())] = 0

                    for x in self.cu_selected_all[i.column()]:
                        if len(x) >= len(self.largest_string_all[i.column()]):
                            self.largest_string_all[i.column()] = x
                            self.largest_text_all[int(i.column())] = len(x) + 1
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

    def selected_rows_2(self, selected, deselected):
        for i in selected.indexes():
            try:
                if int(i.row()) in self.kpi_cells:
                    if int(i.column()) not in self.kpi_cells[int(i.row())]:
                        self.kpi_cells[int(i.row())][int(i.column())] = []
                    self.kpi_cells[int(i.row())][int(i.column())].append(
                        self.kpi_log[int(i.column())][int(i.row())])
                elif int(i.row()) not in self.kpi_cells:
                    self.kpi_cells[int(i.row())] = {}
                    if int(i.column()) not in self.kpi_cells[int(i.row())]:
                        self.kpi_cells[int(i.row())][int(i.column())] = []
                    self.kpi_cells[int(i.row())][int(i.column())].append(
                        self.kpi_log[int(i.column())][int(i.row())])

                cu_value = str(self.ui.table_widget_2.item(
                    i.row(), i.column()).text())
                self.cu_selected_kpi[i.column()].append(cu_value)
                if len(cu_value) >= self.largest_text_kpi[int(i.column())]:
                    self.largest_text_kpi[int(i.column())] = len(cu_value) + 1
                    self.largest_string_kpi[i.column()] = cu_value
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        for i in deselected.indexes():
            try:
                if self.all_cells == {}:
                    pass
                else:
                    # self.kpi_cells[int(i.row())][int(i.column())].remove(self.kpi_log[int(i.column())][int(i.row())])
                    try:
                        del self.kpi_cells[int(i.row())][int(i.column())]
                    except Exception:
                        self.kpi_cells = {}

                    cu_value = str(self.ui.table_widget_2.item(i.row(), i.column()).text())
                    try:
                        self.cu_selected_kpi[int(i.column())].remove(cu_value)
                    except Exception:
                        self.cu_selected_kpi = {0: [], 1: [], 2: [], 3: [], 4: []}

                    # if cu_value == self.largest_string_kpi[i.column()]:
                    self.largest_string_kpi[i.column()] = ''
                    self.largest_text_kpi[int(i.column())] = 0

                    for x in self.cu_selected_kpi[i.column()]:
                        if len(x) >= len(self.largest_string_kpi[i.column()]):
                            self.largest_string_kpi[i.column()] = x
                            self.largest_text_kpi[int(i.column())] = len(x) + 1
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

    def text_changed_starting(self):
        # if text box empty, paste from clipboard on click
        # if text box has text, clear box on click

        text = self.ui.box_starting_mess.text()
        if text == '':
            self.ui.button_clear_1.setText('Paste')
            self.starting_paste = True
        else:
            self.ui.button_clear_1.setText('Clear')
            self.starting_paste = False

    def text_changed_ending(self):
        text = self.ui.box_ending_mess.text()
        if text == '':
            self.ui.button_clear_2.setText('Paste')
            self.ending_paste = True
        else:
            self.ui.button_clear_2.setText('Clear')
            self.ending_paste = False

    def closeEvent(self, event):
        # show warning on clicking close/exit
        close = QMessageBox()
        if self.running is True:
            if self.force_stop != 1:
                self.force_stop -= 1
                close.setText(
                    f"Cannot close! Action ongoing\nTry {self.force_stop} more time to Force Close the App")
                close.setStandardButtons(QMessageBox.Cancel)
                close.setIcon(QMessageBox.Warning)
                close = close.exec()
                event.ignore()
            else:
                event.accept()
        else:
            close.setText("You sure?")
            close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            close.setIcon(QMessageBox.Question)
            close = close.exec()
            if close == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def reload_router(self):
        self.reload_pressed = True
        self.sess.reload_value()
        self.manager.reload_list()

    def exit_detector(self):
        quit = QAction("Quit", self)
        quit.triggered.connect(self.close)

    def reload_kpi(self):
        global accounts
        data_store = open('resource/kpi_id.pckl', 'rb')
        accounts = pickle.load(data_store)
        data_store.close()

    def exiting(self):
        self.close()

    def session_detector(self):
        # check currently available session files

        all_files = []
        self.ui.combobox_session.clear()
        self.ui.combo_session_2.clear()
        for files in os.listdir(os.curdir):
            if files.endswith('session'):
                base_name = os.path.splitext(files)[0]
                all_files.append(base_name)
        if all_files == []:
            self.ui.combobox_session.addItem('Nothing Found')
            self.ui.combobox_session.setCurrentIndex(0)
            self.ui.combo_session_2.addItem('Nothing Found')
            self.ui.combo_session_2.setCurrentIndex(0)
        else:
            self.ui.combobox_session.addItems(all_files)
            self.ui.combobox_session.setCurrentIndex(0)
            self.ui.combo_session_2.addItems(all_files)
            self.ui.combo_session_2.setCurrentIndex(0)

    def edit_box_1(self):
        if self.starting_paste is True:
            self.ui.box_starting_mess.setText(str(pyperclip.paste()))
        else:
            self.ui.box_starting_mess.clear()

    def edit_box_2(self):
        if self.ending_paste is True:
            self.ui.box_ending_mess.setText(str(pyperclip.paste()))
        else:
            self.ui.box_ending_mess.clear()

    def data_parser(self):
        if self.ui.check_create_log.isChecked():
            self.create_log = True
        else:
            self.create_log = False

        starting_data = self.ui.box_starting_mess.text()
        starting_data = "".join(starting_data.split())
        if '/c/' in starting_data:
            self.ui.statusBar().showMessage(f'Private Group Detected')

        ending_data = self.ui.box_ending_mess.text()
        ending_data = "".join(ending_data.split())
        self.cu_session = self.ui.combobox_session.currentText()
        try:
            if starting_data == '':
                pass
            elif 'https://t.me/' not in starting_data:
                self.ui.statusBar().showMessage(
                    f'https://t.me/group_name/message_id is the correct format')
            else:
                if '/c/' in starting_data:
                    starting_data = starting_data.replace('https://t.me/c/', '')
                    starting_data = "".join(starting_data.split())
                    starting_message = starting_data.split('/')
                    self.group_name = starting_message[0]
                    self.group_name = int(f'-100{self.group_name}')
                else:
                    starting_data = starting_data.replace('https://t.me/', '')
                    starting_data = "".join(starting_data.split())
                    starting_message = starting_data.split('/')
                    self.group_name = starting_message[0]
                self.group_starting = int(starting_message[1])

                if ending_data != '' and 'https://t.me/' in ending_data:
                    if '/c/' in ending_data:
                        ending_data = ending_data.replace(
                            'https://t.me/c/', '')
                        ending_data = "".join(ending_data.split())
                        ending_message = ending_data.split('/')
                        self.group_name_2 = ending_message[0]
                        self.group_name_2 = int(f'-100{self.group_name_2}')
                    else:
                        ending_data = ending_data.replace('https://t.me/', '')
                        ending_data = "".join(ending_data.split())
                        ending_message = ending_data.split('/')
                        self.group_name_2 = ending_message[0]
                    self.group_ending = int(ending_message[1])+1

                if ending_data != '' and self.group_name_2 != self.group_name:
                    self.ui.statusBar().showMessage(f'Starting and Ending Group is not the same!')
                else:
                    self.client_starter()
        except Exception as e:
            print(e)
            self.ui.statusBar().showMessage(
                f'Make sure the links are in correct format. Example: https://t.me/TestGroup/123456 or https://t.me/c/123456/123456')

    def counting_label(self):
        if self.cu_dots == '....':
            self.cu_dots = ''
        if self.counting_time == 0:
            self.cu_dots += '.'
            self.ui.statusBar().showMessage(f'Counting{self.cu_dots}')
            self.counting_time = 1
        else:
            self.counting_time -= 1

    def client_starter(self):
        self.reload_kpi()
        while self.ui.table_widget_1.rowCount() > 0:
            self.ui.table_widget_1.removeRow(0)
        while self.ui.table_widget_2.rowCount() > 0:
            self.ui.table_widget_2.removeRow(0)
        self.ui.table_widget_1.setRowCount(5)
        self.ui.table_widget_2.setRowCount(5)
        self.ui.progressBar.setValue(0)
        self.ui.Button_count.setEnabled(False)
        self.ui.button_create_sess.setEnabled(False)
        self.ui.button_send_code.setEnabled(False)
        self.ui.button_reload.setEnabled(False)
        self.ui.button_save.setEnabled(False)
        self.ui.button_remove.setEnabled(False)
        self.ui.button_add_user.setEnabled(False)
        self.ui.progressBar.setValue(0)
        self.running = True
        self.kpi_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.all_log = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.kpi_cells = {}
        self.all_cells = {}
        self.largest_text_all = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        self.largest_text_kpi = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        self.force_stop = 2
        self.thread = QThread()
        self.worker = Worker(self.group_name, self.group_starting,
                             self.group_ending,
                             self.cu_session, self.create_log)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.data_distributor)
        self.worker.list_size.connect(self.row_amount)
        self.worker.row_data.connect(self.set_row_data)
        self.worker.row_data_2.connect(self.set_row_data_kpi)
        self.worker.mess_char.connect(self.total_mess_saver)
        self.worker.finished.connect(self.finishing)
        self.thread.start()

    def data_distributor(self, list_data):
        print(
            f'Bar Value: {list_data[0]}, Total Message: {list_data[1]}, Counter: {list_data[2]}')
        self.progress_bar(int(list_data[0]))
        self.label_changer(int(list_data[1]), int(list_data[2]))
        self.counting_label()

    def progress_bar(self, num):
        self.ui.progressBar.setValue(num)

    def label_changer(self, num_1, num_2):
        self.ui.label_2.setText(f'Total Checked: {num_1}')
        self.ui.label_3.setText(f'KPI Counter: {num_2}')
        self.ui.label_2.adjustSize()
        self.ui.label_3.adjustSize()

    def total_mess_saver(self, user_data):
        user_id = int(user_data[0])
        mess_char = int(user_data[1])

        if user_id not in self.total_mess_char:
            self.total_mess_char[user_id] = mess_char
        else:
            self.total_mess_char[user_id] = self.total_mess_char[user_id] + mess_char

    def finishing(self, total_num):
        self.ui.Button_count.setEnabled(True)
        self.ui.button_create_sess.setEnabled(True)
        self.ui.button_send_code.setEnabled(True)
        self.ui.button_reload.setEnabled(True)
        if self.reload_pressed is True:
            self.ui.button_save.setEnabled(True)
            self.ui.button_remove.setEnabled(True)
            self.ui.button_add_user.setEnabled(True)
        self.group_name = ''
        self.group_name_2 = ''
        self.group_starting = 0
        self.group_ending = 0
        self.cu_session = ''
        self.running = False
        self.force_stop = 3
        self.counting_time = 3
        self.cu_dots = ''
        if total_num[0] == 'incomplete':
            self.ui.total_2.setText(f'Total Message: 0')
            self.ui.total_1.setText(f'Total KPI: 0')
            self.ui.statusBar().showMessage(
                'Incomplete Session. Please create one with Create Session button')
        else:
            self.ui.statusBar().clearMessage()
            self.ui.total_2.setText(f'Total Message: {total_num[0]}')
            self.ui.total_1.setText(f'Total KPI: {total_num[1]}')
        self.ui.table_widget_2.setRowCount(len(self.kpi_log[0]))

    def row_amount(self, num):
        self.ui.table_widget_1.setRowCount(num)
        self.ui.table_widget_2.setRowCount(5)
        self.total_row_all = num

    def set_row_data(self, data):
        average_char = int(self.total_mess_char[int(data[4])] / int(data[2]))
        name = QtWidgets.QTableWidgetItem(str(data[0]))
        username = QtWidgets.QTableWidgetItem(str(data[1]))
        count = QtWidgets.QTableWidgetItem()
        count.setData(QtCore.Qt.DisplayRole, data[2])
        count.setTextAlignment(QtCore.Qt.AlignCenter)
        row_num = data[3]
        user_id = QtWidgets.QTableWidgetItem()
        user_id.setData(QtCore.Qt.DisplayRole, data[4])
        user_id.setTextAlignment(QtCore.Qt.AlignCenter)
        average_count = QtWidgets.QTableWidgetItem()
        average_count.setData(QtCore.Qt.DisplayRole, average_char)
        average_count.setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.table_widget_1.setItem(
            row_num, 0, QtWidgets.QTableWidgetItem(name))
        self.ui.table_widget_1.setItem(
            row_num, 1, QtWidgets.QTableWidgetItem(username))
        self.ui.table_widget_1.setItem(row_num, 2, count)
        self.ui.table_widget_1.setItem(row_num, 3, user_id)
        self.ui.table_widget_1.setItem(row_num, 4, average_count)

        self.all_log[0].append(str(data[0]))
        self.all_log[1].append(str(data[1]))
        self.all_log[2].append(str(data[2]))
        self.all_log[3].append(str(data[4]))
        self.all_log[4].append(str(average_char))

        if self.cu_dots == '....':
            self.cu_dots = ''
        if self.counting_time == 0:
            self.cu_dots += '.'
            self.ui.statusBar().showMessage(f'Finishing Logs{self.cu_dots}')
            self.counting_time = 1
        else:
            self.counting_time -= 1

    def set_row_data_kpi(self, data):
        average_char = int(self.total_mess_char[int(data[4])] / int(data[2]))
        name = QtWidgets.QTableWidgetItem(str(data[0]))
        username = QtWidgets.QTableWidgetItem(str(data[1]))
        count = QtWidgets.QTableWidgetItem()
        count.setData(QtCore.Qt.DisplayRole, data[2])
        count.setTextAlignment(QtCore.Qt.AlignCenter)
        row_num = data[3]
        user_id = QtWidgets.QTableWidgetItem()
        user_id.setData(QtCore.Qt.DisplayRole, data[4])
        user_id.setTextAlignment(QtCore.Qt.AlignCenter)
        average_count = QtWidgets.QTableWidgetItem()
        average_count.setData(QtCore.Qt.DisplayRole, average_char)
        average_count.setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.table_widget_2.setItem(
            row_num, 0, QtWidgets.QTableWidgetItem(name))
        self.ui.table_widget_2.setItem(
            row_num, 1, QtWidgets.QTableWidgetItem(username))
        self.ui.table_widget_2.setItem(row_num, 2, count)
        self.ui.table_widget_2.setItem(row_num, 3, user_id)
        self.ui.table_widget_2.setItem(row_num, 4, average_count)

        self.kpi_log[0].append(str(data[0]))
        self.kpi_log[1].append(str(data[1]))
        self.kpi_log[2].append(str(data[2]))
        self.kpi_log[3].append(str(data[4]))
        self.kpi_log[4].append(str(average_char))
        self.ui.table_widget_2.setRowCount(len(self.kpi_log[0])+1)


class Worker(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(list)
    list_size = pyqtSignal(int)
    row_data = pyqtSignal(list)
    row_data_2 = pyqtSignal(list)
    mess_char = pyqtSignal(list)

    def __init__(self, group_name, group_starting,
                 group_ending, session_name, create_log):
        super().__init__()
        self.pending = 0
        self.cu_session = session_name
        self.last_id = group_ending
        self.group_ending = group_ending
        self.group_name = group_name
        self.group_starting = group_starting
        self.total_mess = 0
        self.counter = 0
        self.mess_value = 0
        self.bar = 0
        self.pending_message = 0
        self.message_data = {}
        self.row_number_all = 0
        self.row_number_kpi = 0
        self.create_log = create_log

    def run(self):
        async def kpi_counter():

            client = TelegramClient(self.cu_session, api_id, api_hash)
            await client.connect()
            me = await client.get_me()
            if me == 'None' or me is None:
                print('Session incomplete')
                self.finished.emit(['incomplete', 'incomplete'])

            else:
                async with client:
                    async for message in client.iter_messages(self.group_name,
                                        offset_id=self.group_ending):
                        mess_len = 0
                        try:
                            mess_sender = message.from_id.user_id
                            if mess_sender in self.message_data:
                                self.message_data[mess_sender] = self.message_data[mess_sender] + 1
                            elif mess_sender not in self.message_data:
                                self.message_data[mess_sender] = 1

                        except Exception as e:
                            print(e)
                        try:
                            if self.last_id != 0:
                                self.total_mess += (self.last_id - message.id)
                                self.pending += self.mess_value * (self.last_id - message.id)
                            else:
                                self.total_mess += 1
                                self.pending += self.mess_value
                            self.last_id = message.id

                            if self.mess_value == 0:
                                if self.group_ending == 0:
                                    self.mess_value_counter(message.id)
                                else:
                                    self.mess_value_counter(self.group_ending)

                            self.pending_message += 1

                            try:
                                mess_text = message.message
                                mess_len = len(str(mess_text))
                                self.mess_char.emit(
                                    [message.from_id.user_id, mess_len])
                                if int(message.id) <= self.group_starting:
                                    self.pending = 100

                                    if '/auscm' in mess_text:
                                        pass
                                    else:
                                        if message.from_id.user_id in accounts:
                                            self.counter += 1
                                    break

                                else:
                                    if '/auscm' in mess_text:
                                        pass
                                    else:
                                        if message.from_id.user_id in accounts:
                                            self.counter += 1

                                if self.pending > 1:
                                    if self.bar != 99:
                                        self.bar += int(self.pending)
                                    self.pending = self.pending - int(self.pending)
                                    self.progress.emit(
                                        [self.bar, self.total_mess,
                                         self.counter])
                                    await asyncio.sleep(0.02)

                                elif self.pending_message > 5:
                                    self.progress.emit(
                                        [self.bar, self.total_mess,
                                         self.counter])
                                    self.pending_message = 0
                                    await asyncio.sleep(0.02)
                            except Exception as e:
                                self.pending += self.mess_value
                                if self.pending_message > 5:
                                    self.progress.emit(
                                        [self.bar, self.total_mess,
                                         self.counter])
                                    self.pending_message = 0
                                # print(e)
                                pass
                        except Exception as e:
                            # print(e)
                            pass

                    if self.bar != 100:
                        self.bar = 100
                        self.pending = self.pending - int(self.pending)
                    self.progress.emit(
                        [self.bar, self.total_mess, self.counter])

                    total_all = 0
                    total_kpi = 0
                    self.message_data = dict(
                        sorted(self.message_data.items(),
                               key=lambda item: item[1]))

                    if self.create_log is True:
                        self.list_size.emit(len(self.message_data))

                        for sender in self.message_data:
                            try:
                                entity = await client.get_entity(sender)
                                id_num = entity.id
                                username = entity.username
                                first_name = entity.first_name
                                last_name = entity.last_name
                                full_name = f'{first_name}'
                                if last_name is not None:
                                    full_name += f' {last_name}'
                                total_all += self.message_data[sender]
                                print(full_name, username,
                                      self.message_data[sender])
                                row_data = [
                                    full_name, username,
                                    self.message_data[sender],
                                    self.row_number_all, id_num]
                                self.row_number_all += 1
                                self.row_data.emit(row_data)

                                if sender in accounts:
                                    row_data = [
                                        full_name, username,
                                        self.message_data[sender],
                                        self.row_number_kpi, id_num]
                                    self.row_number_kpi += 1
                                    self.row_data_2.emit(row_data)
                                    total_kpi += self.message_data[sender]
                            except Exception as e:
                                print(e)

                    self.finished.emit([total_all, total_kpi])
                    await client.disconnect()
                    try:
                        await client.disconnected
                    except OSError:
                        print('Error on disconnect')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(kpi_counter())
        loop.close()

    def mess_value_counter(self, num):
        initial = self.group_starting
        try:
            self.mess_value = 100/(num - initial)
        except Exception as e:
            print(e)
            self.mess_value = 100
        print(num - initial)
        print(self.mess_value)


app = QApplication(sys.argv)
w = main_form()
w.show()
sys.exit(app.exec_())
