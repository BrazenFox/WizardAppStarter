import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread
import webbrowser
import json
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

from enum import Enum

import config
import design


class Buttons(Enum):
    START = "START"
    DB = "DB"
    S = "S"
    P = "P"
    C = "C"
    STOP = "STOP"


class Starter_VM(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)

        self.wizard_starter.add_item("Waiting for VM \"%s\" to power on..." % config.DOCKER_MACHINE_NAME, "ORANGE")
        self.wizard_starter.status_vm = os.system(
            "vboxmanage startvm \"%s\" --type headless" % config.DOCKER_MACHINE_NAME)
        if self.wizard_starter.status_vm == 0:
            self.wizard_starter \
                .switch_buttons([Buttons.STOP, Buttons.DB], True)
            self.wizard_starter \
                .add_item("VM \"%s\" has been successfully started." % config.DOCKER_MACHINE_NAME, "GREEN")
        else:
            self.wizard_starter.vm_not_started()


class Starter_DB(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)
        if self.wizard_starter.status_vm == 0:
            self.wizard_starter \
                .add_item("Waiting for Database \"wizards\" to power on...", "ORANGE")

            while os.system("docker info") == None:
                pass
            self.wizard_starter.status_db = os.system("docker start wizards")
            if self.wizard_starter.status_db == 0:
                self.wizard_starter \
                    .switch_buttons([Buttons.S, Buttons.STOP], True)
                self.wizard_starter \
                    .add_item("Database \"wizards\" has been successfully started.", "GREEN")
            else:
                self.wizard_starter.database_not_started()
        else:
            self.wizard_starter.vm_not_started()


class Starter_S(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)
        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0:
            self.wizard_starter.add_item("Waiting for Server \"WizardApp\" to power on...", "ORANGE")
            self.wizard_starter.status_s = os.system("docker run -d --rm -p 8080:8080 --name wizard-app wizard")
            if self.wizard_starter.status_s == 0:
                self.wizard_starter \
                    .switch_buttons([Buttons.P, Buttons.STOP], True)
                self.wizard_starter.add_item("Server \"WizardApp\" has been successfully started.", "GREEN")
            else:
                self.wizard_starter.server_not_started()
        else:
            if self.wizard_starter.status_vm != 0:
                self.wizard_starter.vm_not_started()
            else:
                self.wizard_starter.database_not_started()


class Starter_P(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)
        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0 and self.wizard_starter.status_s == 0:
            self.wizard_starter.add_item("Waiting for Proxy \"WizardAppGrapQL\" to power on...", "ORANGE")
            self.wizard_starter.status_p = os.system(
                "docker run -d --rm -p 8081:8081/tcp --name my-running-app my-golang-app")
            if self.wizard_starter.status_p == 0:
                self.wizard_starter.add_item("Proxy \"WizardAppGrapQL\" has been successfully started.", "GREEN")
                self.wizard_starter \
                    .switch_buttons([Buttons.C, Buttons.STOP], True)
            else:
                self.wizard_starter.proxy_not_started()
        else:
            if self.wizard_starter.status_vm != 0:
                self.wizard_starter.vm_not_started()
            elif self.wizard_starter.status_db != 0:
                self.wizard_starter.database_not_started()
            else:
                self.wizard_starter.server_not_started()


class Starter_C(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)
        self.wizard_starter.add_item("Waiting for Client \"WizardAppFront\" to power on...", "ORANGE")

        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0 and self.wizard_starter.status_s == 0 and self.wizard_starter.status_p == 0:
            self.wizard_starter.status_c = os.system(
                "docker run -d --rm -p 3000:3000/tcp --name wizard-front-app wizard-front")
            if self.wizard_starter.status_c == 0:
                self.wizard_starter \
                    .switch_buttons([Buttons.STOP], True)
                webbrowser.open("http://192.168.99.102:3000/", new=0)
                self.wizard_starter.add_item("Client \"WizardAppFront\" has been successfully started.", "GREEN")
            else:
                self.wizard_starter.client_not_started()
        else:
            if self.wizard_starter.status_vm != 0:
                self.wizard_starter.vm_not_started()
            elif self.wizard_starter.status_db != 0:
                self.wizard_starter.database_not_started()
            elif self.wizard_starter.status_s != 0:
                self.wizard_starter.server_not_started()
            else:
                self.wizard_starter.proxy_not_started()


class Stop_VM(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter \
            .switch_buttons("ALL", False)

        status = os.system("vboxmanage controlvm \"%s\" poweroff" % config.DOCKER_MACHINE_NAME)
        if status == 0:
            self.wizard_starter.add_item("VM \"%s\" has been successfully stopped." % config.DOCKER_MACHINE_NAME, "RED")
        else:
            self.add_item("VM \"%s\" has not been stopped or already stopped." % config.DOCKER_MACHINE_NAME, "RED")

        self.wizard_starter \
            .switch_buttons([Buttons.STOP, Buttons.START], True)


class WizardStarter(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
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

        self.server_settings = []
        self.proxy_settings = []
        self.client_settings = []

        self.URLDTBS = ''
        self.USR = ''
        self.PASSWORD = ''
        self.SECRET = ''
        self.EXPIRED = ''

        self.ENVURL = ''
        self.ENVINURL = ''
        self.ENVPORT = ''

        self.PROXY = ''
        self.SERVER_URL = ''

        self.read_settings()
        self.write_server_env()
        self.write_proxy_env()
        self.write_client_env()

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

    def add_item(self, string, color):
        item = QListWidgetItem(string)
        item.setForeground(QColor(color))
        self.Info.addItem(item)

    def switch_buttons(self, array, case):
        if array == "ALL":
            self.Start.setDisabled(True) if not case else self.Start.setEnabled(True)
            self.Database.setDisabled(True) if not case else self.Database.setEnabled(True)
            self.Server.setDisabled(True) if not case else self.Server.setEnabled(True)
            self.Proxy.setDisabled(True) if not case else self.Proxy.setEnabled(True)
            self.Client.setDisabled(True) if not case else self.Client.setEnabled(True)
            self.Stop.setDisabled(True) if not case else self.Stop.setEnabled(True)
        else:
            for i in array:
                if i.name == "START":
                    self.Start.setDisabled(True) if not case else self.Start.setEnabled(True)
                if i.name == "DB":
                    self.Database.setDisabled(True) if not case else self.Database.setEnabled(True)
                if i.name == "S":
                    self.Server.setDisabled(True) if not case else self.Server.setEnabled(True)
                if i.name == "P":
                    self.Proxy.setDisabled(True) if not case else self.Proxy.setEnabled(True)
                if i.name == "C":
                    self.Client.setDisabled(True) if not case else self.Client.setEnabled(True)
                if i.name == "STOP":
                    self.Stop.setDisabled(True) if not case else self.Stop.setEnabled(True)

    def vm_not_started(self):
        self.switch_buttons([Buttons.START, Buttons.STOP], True)
        self.add_item("VM \"%s\" has not been started." % config.DOCKER_MACHINE_NAME, "RED")

    def database_not_started(self):
        self.switch_buttons([Buttons.DB, Buttons.STOP], True)
        self.add_item("Database \"wizards\" has not been started.", "RED")

    def server_not_started(self):
        self.switch_buttons([Buttons.S, Buttons.STOP], True)
        self.add_item("Server \"WizardApp\" has not been started.", "RED")

    def proxy_not_started(self):
        self.switch_buttons([Buttons.P, Buttons.STOP], True)
        self.add_item("Proxy \"WizardAppGraphQL\" has not been started.", "RED")

    def client_not_started(self):
        self.switch_buttons([Buttons.C, Buttons.STOP], True)
        self.add_item("Client \"WizardAppFront\" has not been started.", "RED")

    def read_settings(self):
        with open('settings.txt') as json_file:
            data = json.load(json_file)
            server = data['server']
            self.URLDTBS = 'URLDTBS=' + server['URLDTBS']
            self.USR = 'USR=' + server['USR']
            self.PASSWORD = 'PASSWORD=' + server['PASSWORD']
            self.SECRET = 'SECRET=' + server['SECRET']
            self.EXPIRED = 'EXPIRED=' + server['EXPIRED']
            proxy = data['proxy']
            self.ENVURL = 'ENVURL=' + proxy['ENVURL']
            self.ENVINURL = 'ENVINURL=' + proxy['ENVINURL']
            self.ENVPORT = 'ENVPORT=' + proxy['ENVPORT']
            client = data['client']
            self.PROXY = 'PROXY=' + client['PROXY']
            self.SERVER_URL = 'SERVER_URL=' + client['SERVER_URL']

    def write_server_env(self):
        server_env = open('server_env.list', 'w')
        server_env.write(self.URLDTBS + '\n')
        server_env.write(self.USR + '\n')
        server_env.write(self.PASSWORD + '\n')
        server_env.write(self.SECRET + '\n')
        server_env.write(self.EXPIRED + '\n')

    def write_proxy_env(self):
        proxy_env = open('proxy_env.list', 'w')
        proxy_env.write(self.ENVURL + '\n')
        proxy_env.write(self.ENVINURL + '\n')
        proxy_env.write(self.ENVPORT + '\n')

    def write_client_env(self):
        client_env = open('client_env.list', 'w')
        client_env.write(self.PROXY + '\n')
        client_env.write(self.SERVER_URL + '\n')


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = WizardStarter()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
# pyinstaller --onefile --icon=wizard.ico --noconsole main.pyw
