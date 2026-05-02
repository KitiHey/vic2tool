from PySide6.QtWidgets import QMessageBox
import os

def errorOut(parent, error: str):
    QMessageBox.critical(parent, "Error", error)

def succededOut(parent, message: str):
    QMessageBox.information(parent, "Success!", message)

def getFile(path, filename) -> str:
    newpath = path
    if (path[len(path)-1] != "/"):
        newpath += "/"
    newpath += filename
    if not os.path.exists(newpath):
        raise FileNotFoundError(f"Error, file {newpath} does not exist")
    return newpath
