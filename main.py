from PySide6.QtWidgets import QApplication, QLabel, QWidget
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
#path = SelectPath()
#if path == "":
#    exit(0)
path = "/home/kitihey/Descargas/Victoria.II.v3.04.Inclu.ALL.DLC/mod/partidos randoms"

loader = QUiLoader()
for widget in custom_widgets.widgets:
    loader.registerCustomWidget(widget)
window = loader.load("ui/mainwindow.ui", None)

builder = ProvinceBuilder(path) \
            .removeProvinceColors() \
            .removeSea()
window.popSelectorImg.setPixmap(builder.getPixmap())

def clickedSelector(x, y):
    if builder.provinceIsSea(x, y):
        return
    color = builder.getProvincePixel(x, y)
    if builder.provinceIsSelected(x, y):
        builder.deselectProvince(color)
    else:
        builder.selectProvince(color)

    window.popSelectorImg.setPixmap(builder.getPixmap())
    window.popChanged.setText(str(builder.population()))
    window.currentPop.setText(str(builder.population()))
    window.removedPop.setText("0")
    window.selectedProvinces.setText(", ".join(builder.selectedProvinces()))
def changePop():
    try:
        txt = str(eval(window.popChanged.text()))
    except:
        txt = window.currentPop.text()
    window.popChanged.setText(txt)
    window.removedPop.setText(str(int(float(window.currentPop.text())-float(txt))))


window.popSelectorImg.installEventFilter(window)
window.popSelectorImg.clicked.connect(clickedSelector)
window.popChanged.returnPressed.connect(changePop)

window.show()
app.exec()
