import os
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
import webbrowser
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
            self.wizard_starter.Database.setEnabled(True)
            self.wizard_starter.Start.setDisabled(True)


class Starter_DB(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter.Start.setDisabled(True)
        self.wizard_starter.Stop.setDisabled(True)

        if self.wizard_starter.status_vm == 0:
            while os.system("docker info") == None:
                pass
            self.wizard_starter.status_db = os.system("docker start wizards")
            if self.wizard_starter.status_db == 0:
                self.wizard_starter.Database.setDisabled(True)
                self.wizard_starter.Server.setEnabled(True)
            self.wizard_starter.Stop.setEnabled(True)

class Starter_S(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter
    def run(self):
        self.wizard_starter.Stop.setDisabled(True)
        if self.wizard_starter.status_db == 0:
            self.wizard_starter.status_s = os.system("docker run -d --rm -p 8080:8080 --name wizard-app wizard")
            self.wizard_starter.Stop.setEnabled(True)
            self.wizard_starter.Proxy.setEnabled(True)

class Starter_P(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter
    def run(self):
        self.wizard_starter.Stop.setDisabled(True)
        if self.wizard_starter.status_s == 0:
            self.wizard_starter.status_p = os.system("docker run -d --rm -p 8081:8081/tcp --name my-running-app my-golang-app")
            self.wizard_starter.Stop.setEnabled(True)
            self.wizard_starter.Client.setEnabled(True)

class Starter_C(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter
    def run(self):
        self.wizard_starter.Stop.setDisabled(True)
        if self.wizard_starter.status_p == 0:
            self.wizard_starter.status_c = os.system("docker run -d --rm -p 3000:3000/tcp --name wizard-front-app wizard-front")
            webbrowser.open("http://192.168.99.102:3000/", new=0)
            self.wizard_starter.Stop.setEnabled(True)
            self.wizard_starter.Client.setEnabled(True)


class Stop_VM(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        os.system("vboxmanage controlvm \"%s\" poweroff" % config.DOCKER_MACHINE_NAME)
        self.wizard_starter.Start.setEnabled(True)


class WizardStarter(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.Start.clicked.connect(self.start)
        self.Database.clicked.connect(self.database)
        self.Server.clicked.connect(self.server)
        self.Proxy.clicked.connect(self.proxy)
        self.Client.clicked.connect(self.client)
        self.Stop.clicked.connect(self.stop)

        self.status_vm = None
        self.status_db = None
        self.status_s = None
        self.status_p = None
        self.status_c = None

        self.Starter_VM = Starter_VM(wizard_starter=self)
        self.Starter_DB = Starter_DB(wizard_starter=self)
        self.Starter_S = Starter_S(wizard_starter=self)
        self.Starter_P = Starter_P(wizard_starter=self)
        self.Starter_C = Starter_C(wizard_starter=self)
        self.Stop_VM = Stop_VM(wizard_starter=self)

    def start(self):
        self.Starter_VM.start()

    def database(self):
        self.Starter_DB.start()

    def server(self):
        self.Starter_S.start()

    def proxy(self):
        self.Starter_P.start()

    def client(self):
        self.Starter_C.start()

    def stop(self):
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
#pyinstaller --onefile --icon=wizard.ico --noconsole main.pyw