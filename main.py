from PySide6.QtWidgets import QApplication, QLabel, QWidget, QMessageBox
from PySide6.QtUiTools import QUiLoader
import os

def errorOut(parent, error: str):
    QMessageBox.critical(parent, "Error", error)

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
window = loader.load("ui/mainwindow.ui", None)

window.show()
app.exec()
