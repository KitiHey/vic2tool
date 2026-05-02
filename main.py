from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QObject
from province import ProvinceBuilder
from utilities import errorOut
import custom_widgets
import os

def SelectPath() -> str:
    loader = QUiLoader()
    window = loader.load("ui/initwindow.ui", None)
    window.show()

    pathSelector = window.pathSelector
    def select():
        text = pathSelector.text()
        if not os.path.isdir(text):
            errorOut(window, "The inserted path is either not correct or not a directory")
            return
        app.quit()

    pathSelector.returnPressed.connect(select)
    app.exec()
    return pathSelector.text()

app = QApplication([])
path = SelectPath()
if path == "":
    exit(0)

loader = QUiLoader()
for widget in custom_widgets.widgets:
    loader.registerCustomWidget(widget)
window = loader.load("ui/mainwindow.ui", None)

try:
    builder = ProvinceBuilder(path) \
                .removeProvinceColors() \
                .removeSea()
except FileNotFoundError as e:
    errorOut(window, str(e))
    exit(0)
popSelector(window, builder)

window.show()
app.exec()
