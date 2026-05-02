from PySide6.QtWidgets import QMessageBox

def errorOut(parent, error: str):
    QMessageBox.critical(parent, "Error", error)

def getFile(path, filename) -> str:
    newpath = path
    if (path[len(path)-1] != "/"):
        newpath += "/"
    newpath += filename
    return newpath
