from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings
import Config


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)

        uic.loadUi('ui/settings.ui', self)

        contents = self.findChild(QtWidgets.QWidget, 'scrollAreaWidgetContents')
        layout = QtWidgets.QVBoxLayout()
        contents.setLayout(layout)

        for section in Config.settings:
            title = QtWidgets.QLabel(section['title'])
            layout.addWidget(title)

            formLayoutWidget = QtWidgets.QWidget()
            form = QtWidgets.QFormLayout()
            formLayoutWidget.setLayout(form)

            for field in section['fields']:
                edit = QtWidgets.QLineEdit(str(field['value']))
                edit.setObjectName(field['id'])
                form.addRow(field['name'], edit)

            layout.addWidget(formLayoutWidget)

        layout.insertStretch(-1)

        self.btnSave = self.findChild(QtWidgets.QPushButton, 'btnSave')
        self.btnSave.clicked.connect(self.accept)

        self.btnCancel = self.findChild(QtWidgets.QPushButton, 'btnCancel')
        self.btnCancel.clicked.connect(self.reject)

    def accept(self):
        super(SettingsWindow, self).accept()

        savedSettings = QSettings('config/config.ini', QSettings.IniFormat)

        for section in Config.settings:
            for field in section['fields']:
                valueEdit = self.findChild(QtWidgets.QLineEdit, field['id'])

                if field['type'] == int:
                    field['value'] = int(valueEdit.text())
                elif field['type'] == float:
                    field['value'] = float(valueEdit.text())

                print(f"{field['name']}: {field['value']}")
                savedSettings.setValue(field['id'], field['value'])

        del savedSettings  # this *saves* the file. i promise! it says del, but it actually writes the file out.
