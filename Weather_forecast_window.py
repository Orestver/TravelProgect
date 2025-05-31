from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from weather_forecast import WeatherForecast
import sys
class WeatherWindow(QWidget):

    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Погода")
        
        self.setGeometry(0, 0, 400, 1000)
        self.setStyleSheet("""
        QWidget {
            background-color: #cfc880;
        }
    """)

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignCenter)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)


        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Введіть місто")
        self.city_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
        """)

        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 14))
        self.result_label.setStyleSheet("color: white;")
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignCenter)

        self.get_weather_btn = QPushButton("Показати погоду")
        self.get_weather_btn.setStyleSheet("""
            QPushButton {
                background-color: #c7b37d;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #a58b5e;
            }
        """)
        self.get_weather_btn.clicked.connect(self.fetch_weather)

        self.close_btn = QPushButton("Закрити")
        self.close_btn.setStyleSheet("background-color: #a94442; color: white; font-size: 14px; padding: 8px; border-radius: 6px;")
        self.close_btn.clicked.connect(self.close)

        self.content_layout.addWidget(self.city_input)
        self.content_layout.addWidget(self.get_weather_btn)
        self.content_layout.addWidget(self.result_label)
        self.content_layout.addWidget(self.close_btn)

        self.content_widget.resize(self.size())
        # Підключення класу погоди
        self.weather = WeatherForecast(parent=self, label=self.result_label)

    def fetch_weather(self):
        city = self.city_input.text().strip().title()
        self.weather.get_weather(city)

    def resizeEvent(self, event):
        self.content_widget.resize(self.size())
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherWindow()
    window.show()
    sys.exit(app.exec_())
