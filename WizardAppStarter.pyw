import os
import sys
import webbrowser
from enum import Enum
import yaml
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

import design

DOCKER_INFO = "docker info"
DOCKER_DATABASE_START = "docker start wizards"

DOCKER_MACHINE_NAME = os.environ.get('DOCKER_MACHINE_NAME')
DOCKER_MACHINE_HOST = os.environ.get('NO_PROXY')


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
        self.wizard_starter.switch_buttons("ALL", False)
        self.wizard_starter.add_item("Waiting for VM \"%s\" to power on..." % DOCKER_MACHINE_NAME, "ORANGE")
        self.wizard_starter.status_vm = os.system("vboxmanage startvm \"%s\" --type headless" % DOCKER_MACHINE_NAME)
        if self.wizard_starter.status_vm == 0:
            self.wizard_starter.switch_buttons([Buttons.STOP, Buttons.DB], True)
            self.wizard_starter.add_item("VM \"%s\" has been successfully started." % DOCKER_MACHINE_NAME, "GREEN")
        else:
            self.wizard_starter.vm_not_started()


class Starter_DB(QThread):
    def __init__(self, wizard_starter, parent=None):
        super().__init__()
        self.wizard_starter = wizard_starter

    def run(self):
        self.wizard_starter.switch_buttons("ALL", False)

        if self.wizard_starter.status_vm == 0:
            self.wizard_starter.add_item("Waiting for Database \"wizards\" to power on...", "ORANGE")

            while os.system(DOCKER_INFO) == None:
                pass
            self.wizard_starter.status_db = os.system(DOCKER_DATABASE_START)
            if self.wizard_starter.status_db == 0:
                self.wizard_starter.switch_buttons([Buttons.S, Buttons.STOP], True)
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
        self.wizard_starter.set_settings()
        self.wizard_starter.switch_buttons("ALL", False)
        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0:
            self.wizard_starter.add_item("Waiting for Server \"WizardApp\" to power on...", "ORANGE")
            self.wizard_starter.status_s = os.system(self.wizard_starter.server_docker_run)
            if self.wizard_starter.status_s == 0:
                self.wizard_starter.switch_buttons([Buttons.P, Buttons.STOP], True)
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
        self.wizard_starter.switch_buttons("ALL", False)
        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0 and self.wizard_starter.status_s == 0:
            self.wizard_starter.add_item("Waiting for Proxy \"WizardAppGrapQL\" to power on...", "ORANGE")
            self.wizard_starter.status_p = os.system(self.wizard_starter.proxy_docker_run)
            if self.wizard_starter.status_p == 0:
                self.wizard_starter.add_item("Proxy \"WizardAppGrapQL\" has been successfully started.", "GREEN")
                self.wizard_starter.switch_buttons([Buttons.C, Buttons.STOP], True)
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
        self.wizard_starter.switch_buttons("ALL", False)
        self.wizard_starter.add_item("Waiting for Client \"WizardAppFront\" to power on...", "ORANGE")

        if self.wizard_starter.status_vm == 0 and self.wizard_starter.status_db == 0 and self.wizard_starter.status_s == 0 and self.wizard_starter.status_p == 0:
            self.wizard_starter.status_c = os.system(self.wizard_starter.client_docker_run)
            if self.wizard_starter.status_c == 0:
                self.wizard_starter.switch_buttons([Buttons.STOP], True)
                webbrowser.open("http://" + DOCKER_MACHINE_HOST + ":" + self.wizard_starter.client_port + "/", new=0)
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
        self.wizard_starter.switch_buttons("ALL", False)

        status = os.system("vboxmanage controlvm \"%s\" poweroff" % DOCKER_MACHINE_NAME)
        if status == 0:
            self.wizard_starter.add_item("VM \"%s\" has been successfully stopped." % DOCKER_MACHINE_NAME, "RED")
        else:
            self.wizard_starter.add_item("VM \"%s\" has not been stopped or already stopped." % DOCKER_MACHINE_NAME, "RED")

        self.wizard_starter.switch_buttons([Buttons.STOP, Buttons.START], True)


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

        self.server_docker_run = ""
        self.proxy_docker_run = ""
        self.client_docker_run = ""
        self.client_port = ""
        self.server_port = ""
        self.proxy_port = ""

        self.set_settings()

        self.ServerPortInput.setText('http://' + DOCKER_MACHINE_HOST + ':' + self.server_port)
        self.ServerPortInput.setReadOnly(True)
        self.ProxyPortInput.setText('http://' + DOCKER_MACHINE_HOST + ':' + self.proxy_port + '/query')
        self.ProxyPortInput.setReadOnly(True)
        self.ClientPortInput.setText('http://' + DOCKER_MACHINE_HOST + ':' + self.client_port)
        self.ClientPortInput.setReadOnly(True)

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
        self.add_item("VM \"%s\" has not been started." % DOCKER_MACHINE_NAME, "RED")

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

    def set_settings(self):
        with open('settings.yaml') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            server = data['server']
            proxy = data['proxy']
            client = data['client']

            self.server_docker_run = "docker run -d"
            self.server_docker_run = self.server_docker_run + " -e " + 'URLDTBS=' + server['URLDTBS']
            self.server_docker_run = self.server_docker_run + " -e " + 'USR=' + server['USR']
            self.server_docker_run = self.server_docker_run + " -e " + 'PASSWORD=' + server['PASSWORD']
            self.server_docker_run = self.server_docker_run + " -e " + 'SECRET=' + server['SECRET']
            self.server_docker_run = self.server_docker_run + " -e " + 'EXPIRED=' + str(server['EXPIRED'])
            self.server_docker_run = self.server_docker_run + " --rm -p %s:8080 --name wizard-app wizard" % str(server['PORT'])
            self.server_port = str(server['PORT'])

            self.proxy_docker_run = "docker run -d"
            self.proxy_docker_run = self.proxy_docker_run + " -e " + 'ENVURL=http://' + DOCKER_MACHINE_HOST + ':' + str(server['PORT'])
            self.proxy_docker_run = self.proxy_docker_run + " -e " + 'ENVINURL=http://' + DOCKER_MACHINE_HOST + ':' + str(client['PORT'])
            self.proxy_docker_run = self.proxy_docker_run + " --rm -p %s:8081 --name my-running-app my-golang-app" % str(proxy['PORT'])
            self.proxy_port = str(proxy['PORT'])

            self.client_docker_run = "docker run -d"
            self.client_docker_run = self.client_docker_run + " -e " + 'SERVER_URL=http://' + DOCKER_MACHINE_HOST + ':' + str(proxy['PORT']) + "/query"
            self.client_docker_run = self.client_docker_run + " --rm -p %s:3000 --name wizard-front-app wizard-front" % str(client['PORT'])
            self.client_port = str(client['PORT'])


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = WizardStarter()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
# pyinstaller --onefile --icon=wizard.ico --noconsole WizardAppStarter.pyw
