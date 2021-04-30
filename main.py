import os
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
import config
import design  # Это наш конвертированный файл дизайна


class Starter_VM(QtCore.QObject):
    addItem = QtCore.pyqtSignal(str)

    def start_VM(self):
        self.addItem.emit("Start")
        status_vm = os.system("vboxmanage startvm \"%s\" --type headless" % config.DOCKER_MACHINE_NAME)
        if status_vm == 0:

            while os.system("docker info") == None:
                pass

            status_db = os.system("docker start wizards")
            print(status_db)
            os.system("echo docker start server")
            os.system("echo docker start proxy")
            os.system("echo docker start client")

    def stop_VM(self):
        self.addItem.emit("Stop")
        os.system("vboxmanage controlvm \"%s\" poweroff" % config.DOCKER_MACHINE_NAME)


class WizardStarter(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.Start.clicked.connect(self.start_app)
        self.Stop.clicked.connect(self.stop_app)

        self.thread = QtCore.QThread()
        self.starter_VM = Starter_VM()
        self.starter_VM.moveToThread(self.thread)
        self.starter_VM.addItem.connect(self.add_item)
        self.thread.started.connect(self.starter_VM.start_VM)
        self.thread.finished.connect(self.starter_VM.stop_VM)

    def start_app(self):
        self.Start.setDisabled(True)
        self.thread.start()

    def stop_app(self):
        self.Start.setEnabled(True)
        self.thread.quit()

    def add_item(self, string):
        self.Info.addItem(string)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = WizardStarter()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
