from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QGridLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QFont, QPixmap, QIcon
import sys,os


def resorse_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_UI()
        

    def init_window(self):
        self.setWindowTitle("EasyJourney")
        self.setGeometry(0, 0, 1920, 1200)
        self.setWindowIcon(QIcon(resorse_path("assets/LOGO.jpg")))
        

    def init_UI(self):
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap(resorse_path("assets/TRAVEL_LOGO.jpg")))
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())
        
        self.content_widget = QWidget(self)
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.content_layout.setContentsMargins(50, 50, 50, 50)
        self.content_layout.setSpacing(20)

        self.label = QLabel("EasyJourney")
        self.label.setFont(QFont("Algerian", 40))
        self.label.setStyleSheet("color: #c7b37d;")
        self.label.setAlignment(Qt.AlignCenter)

        self.button1 = QPushButton("Дізнатися погоду")
        self.button1.setStyleSheet(self.btn_style())
        
        self.button1.setEnabled(False)

        self.button_graph = QPushButton("Знайти маршрут")
        self.button_graph.setStyleSheet(self.btn_style())
        
        self.button_graph.setEnabled(False)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 14px; color: white;")
        self.result_label.setWordWrap(True)

        self.reg_button = QPushButton("Зареєструватися")
        self.reg_button.setStyleSheet(self.btn_style())
        
        self.reg_button.setEnabled(True)

        self.log_button = QPushButton("Авторизуватися")
        self.log_button.setStyleSheet(self.btn_style())
        
        self.log_button.setEnabled(True)

        self.plan_button = QPushButton("Скласти план відпочинку")
        self.plan_button.setStyleSheet(self.btn_style())
        
        self.plan_button.setEnabled(False)

        self.content_layout.addWidget(self.label, 0, 0, 1, 5)
        self.content_layout.addWidget(self.button1, 1, 0)
        self.content_layout.addWidget(self.button_graph, 1, 1)
        self.content_layout.addWidget(self.log_button,1, 2)
        self.content_layout.addWidget(self.reg_button, 1, 3)
        self.content_layout.addWidget(self.result_label, 3, 0)
        self.content_layout.addWidget(self.plan_button, 1, 4)

        self.content_widget.resize(self.size())
    def btn_style(self):
        return """
            QPushButton {
                background-color: #c7b37d;
                color: white;
                font-size: 18px;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #a58b5e;
            }
        """
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.showMaximized() 
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
