import os
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread

import config
import design  # Это наш конвертированный файл дизайна


class Starter_VM(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter.Stop.setDisabled(True)
        self.wizard_starter.status_vm = os.system(
            "vboxmanage startvm \"%s\" --type headless" % config.DOCKER_MACHINE_NAME)
        if self.wizard_starter.status_vm == 0:
            self.wizard_starter.Stop.setEnabled(True)


class Starter_DB(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        if self.wizard_starter.self.status_vm == 0:
            while os.system("docker info") == None:
                pass
            self.wizard_starter.status_db = os.system("docker start wizards")


class Stop_VM(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        os.system("vboxmanage controlvm \"%s\" poweroff" % config.DOCKER_MACHINE_NAME)


class WizardStarter(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.Start.clicked.connect(self.start_app)
        self.Stop.clicked.connect(self.stop_app)

        self.status_vm = None
        self.status_db = None
        self.status_s = None
        self.status_p = None
        self.status_c = None

        self.Starter_VM = Starter_VM(wizard_starter=self)
        self.Starter_DB = Starter_DB(wizard_starter=self)
        self.Stop_VM = Stop_VM(wizard_starter=self)

    def start_app(self):
        self.Start.setDisabled(True)
        self.Starter_VM.start()

    def stop_app(self):
        self.Start.setEnabled(True)
        self.Stop_VM.start()

    def add_item(self, string):
        self.Info.addItem(string)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = WizardStarter()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
