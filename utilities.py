from PySide6.QtWidgets import QMessageBox
import os
from time import time

def timeBench(function):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = function(*args, **kwargs)
        t2 = time()
        print(f"Function '{function.__name__!r}' executed in {(t2-t1):.4f}s")
        return result
    return wrapper

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
