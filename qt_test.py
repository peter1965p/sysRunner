from PySide6.QtWidgets import QApplication, QMainWindow

print("QT TEST START…")

app = QApplication([])

win = QMainWindow()
win.setWindowTitle("Qt Test")
win.resize(800, 600)
win.show()

app.exec()
