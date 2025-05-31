import sys,os
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QGridLayout, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWebEngineWidgets import QWebEngineView


from Weather_forecast_window import WeatherWindow
from graph import CityNavigator, RouteWindow
from config import HOST,USER,PASSWORD,DATABASE
from travel_assistant import AssistantWindow
import re
import bcrypt


def resorse_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)





class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def create_database(self):
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL
                )
            """)
            print("✅ База даних та таблиця створені успішно.")
            cursor.close()
            conn.close()
        except Error as e:
            print("❌ Помилка підключення до MySQL:", e)

    def register_user(self, username, email, password):
        conn = None
        cursor = None
        try:
            print("📦 Підключення до бази...")
            conn = mysql.connector.connect(
                host=self.host, user=self.user,
                password=self.password, database=self.database
            )
            print("✅ Підключено до бази")
            cursor = conn.cursor()
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password))
            conn.commit()
            print("✅ Користувач зареєстрований успішно!")
        except mysql.connector.IntegrityError as e:
            print("⚠️ IntegrityError:", e)
            raise e
        except Error as e:
            print("❌ Error при підключенні до бази:", e)
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def login_user(self, email, password):
        try:
            conn = mysql.connector.connect(
                host=self.host, user=self.user,
                password=self.password, database=self.database
            )
            cursor = conn.cursor()
            
            
            cursor.execute("SELECT username, password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                username, hashed_password = result
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    print(f"👋 Вітаємо, {username}! Вхід успішний.")
                    return True, username
                else:
                    print("❌ Невірний пароль.")
            else:
                print("❌ Користувача не знайдено.")

            return False, "Невірний email або пароль"
        except Error as e:
            print("❌ Помилка:", e)
            return False, str(e)


class RegisterUser(QObject):
    finished = pyqtSignal(bool, str)

    def __init__(self, db, username, email, password):
        super().__init__()
        self.db = db
        self.username = username
        self.email = email
        self.password = password

    def run(self):
        try:
            self.db.register_user(self.username, self.email, self.password)
            self.finished.emit(True, "Користувач успішно зареєстрований!")
        except Exception as e:
            self.finished.emit(False, str(e))

class LoginUser(QObject):
    finished = pyqtSignal(bool,str)
    def __init__(self, db, email, password):
        super().__init__()
        self.db = db
        self.email = email
        self.password = password
    def run_log(self):
        try:
            success, message = self.db.login_user(self.email, self.password)
            self.finished.emit(success, message if success else "Невірний email або пароль спробуйте щераз")
        except Exception as e:
            self.finished.emit(False, str(e))



class Register_window(QWidget):
    registration_successful = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database(HOST, USER, PASSWORD, DATABASE)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Реєстрація")
        self.setGeometry(1520, 29, 400, 1000)
        self.setStyleSheet("background-color: #cfc880;")

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignCenter)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)

        # Поля вводу
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введіть ім’я користувача")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введіть емейл")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введіть пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Стиль полів
        field_style = """
            QLineEdit {
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
        """
        self.username_input.setStyleSheet(field_style)
        self.email_input.setStyleSheet(field_style)
        self.password_input.setStyleSheet(field_style)

        # Кнопка реєстрації
        self.register_btn = QPushButton("Зареєструватися")
        self.register_btn.setStyleSheet("""
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
        self.register_btn.clicked.connect(self.submit_reg_form)

        # Кнопка закриття
        self.close_btn = QPushButton("Закрити")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #a94442;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7b312e;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        # Додавання елементів
        self.content_layout.addWidget(QLabel("Ім’я користувача:"))
        self.content_layout.addWidget(self.username_input)
        self.content_layout.addWidget(QLabel("Емейл:"))
        self.content_layout.addWidget(self.email_input)
        self.content_layout.addWidget(QLabel("Пароль (мін 8 символів):"))
        self.content_layout.addWidget(self.password_input)
        self.content_layout.addWidget(self.register_btn)
        self.content_layout.addWidget(self.close_btn)

        self.content_widget.resize(self.size())

    def is_valid_email(self,email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)
    def is_valid_password(self,password):
        if len(password) >= 8:
            return True
        else:
            return False
    def submit_reg_form(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть усі поля!")
            return
        if not self.is_valid_email(email):
            QMessageBox.critical(self, "Помилка", "Неправильний формат емейлу!")
            return
        if not self.is_valid_password(password):
            QMessageBox.critical(self, "Помилка", "Пароль повинен містити мінімум 8 символів!")
            return
        

        self.thread = QThread()
        self.worker = RegisterUser(self.db, username, email, password)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_register_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_register_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Успішна реєстрація", message)
            self.registration_successful.emit() 
            self.close() 
        else:
            QMessageBox.critical(self, "Помилка", message)

    def resizeEvent(self, event):
        self.content_widget.resize(self.size())
        super().resizeEvent(event)


class Login_window(QWidget):
    login_successful = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.InitUI()
        self.db = Database(HOST, USER, PASSWORD, DATABASE)

    def InitUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Вхід")
        self.setGeometry(1520, 29, 400, 1000)
        self.setStyleSheet("background-color: #cfc880;")

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignCenter)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)
    
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введіть емейл")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введіть пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Стиль полів
        field_style = """
            QLineEdit {
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
        """
        self.email_input.setStyleSheet(field_style)
        self.password_input.setStyleSheet(field_style)
        
        self.login_btn = QPushButton("Авторизуватися")
        self.login_btn.setStyleSheet("""
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
        self.login_btn.clicked.connect(self.submit_log_form)

        # Кнопка закриття
        self.close_btn = QPushButton("Закрити")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #a94442;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7b312e;
            }
        """)
        self.close_btn.clicked.connect(self.close)

    
        self.content_layout.addWidget(QLabel("Емейл:"))
        self.content_layout.addWidget(self.email_input)
        self.content_layout.addWidget(QLabel("Пароль:"))
        self.content_layout.addWidget(self.password_input)
        self.content_layout.addWidget(self.login_btn)
        self.content_layout.addWidget(self.close_btn)

        self.content_widget.resize(self.size())

    def submit_log_form(self):

        email = self.email_input.text()
        password = self.password_input.text()

        self.thread = QThread()
        self.worker = LoginUser(self.db, email, password)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run_log)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_login_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Успішний вхід", message)
            self.login_successful.emit()
            self.close() 
        else:
            QMessageBox.critical(self, "Помилка", message)

    def resizeEvent(self, event):
        self.content_widget.resize(self.size())
        super().resizeEvent(event)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.builder = CityNavigator(resorse_path("assets/worldcities.xlsx"), parent=self)
        self.is_autorized = False
        self.init_window()
        self.init_UI()
        self.show_route_on_map([])  

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
        self.button1.clicked.connect(self.open_weather_window)
        self.button1.setEnabled(False)

        self.button_graph = QPushButton("Знайти маршрут")
        self.button_graph.setStyleSheet(self.btn_style())
        self.button_graph.clicked.connect(self.open_route_dialog)
        self.button_graph.setEnabled(False)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 14px; color: white;")
        self.result_label.setWordWrap(True)

        self.reg_button = QPushButton("Зареєструватися")
        self.reg_button.setStyleSheet(self.btn_style())
        self.reg_button.clicked.connect(self.open_register_window)
        self.reg_button.setEnabled(True)

        self.log_button = QPushButton("Авторизуватися")
        self.log_button.setStyleSheet(self.btn_style())
        self.log_button.clicked.connect(self.open_login_window)
        self.log_button.setEnabled(True)

        self.plan_button = QPushButton("Скласти план відпочинку")
        self.plan_button.setStyleSheet(self.btn_style())
        self.plan_button.clicked.connect(self.open_assistant_window)
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
    def on_authenticated(self):
        self.is_autorized = True
        self.button_graph.setEnabled(self.is_autorized)
        self.button1.setEnabled(self.is_autorized)
        self.plan_button.setEnabled(self.is_autorized)

    def open_register_window(self):
        self.reg_db = Register_window()
        self.reg_db.setAttribute(Qt.WA_DeleteOnClose)
        self.reg_db.registration_successful.connect(self.on_authenticated)
        self.reg_db.show()
        
    def open_assistant_window(self):
        self.assist = AssistantWindow()
        self.assist.setAttribute(Qt.WA_DeleteOnClose)
        self.assist.show()


    def open_login_window(self):
        self.log_db = Login_window()
        self.log_db.setAttribute(Qt.WA_DeleteOnClose)
        self.log_db.login_successful.connect(self.on_authenticated)
        self.log_db.show()
        

    def open_route_dialog(self):
        self.route_window = RouteWindow(self.builder, self)
        self.route_window.show()

    def open_weather_window(self):
        self.weather_window = WeatherWindow(parent=self)
        self.weather_window.setAttribute(Qt.WA_DeleteOnClose)
        self.weather_window.show()


    def show_route_on_map(self, path):
        if hasattr(self, 'map_view'):
            self.content_layout.removeWidget(self.map_view)
            self.map_view.deleteLater()
            del self.map_view

        self.map_container = QWidget()
        map_layout = QVBoxLayout(self.map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)

        close_button = QPushButton("Закрити карту")
        close_button.setStyleSheet("background-color: #a94442; color: white; font-size: 14px; padding: 8px; border-radius: 6px;")
        close_button.clicked.connect(self.close_map)

        self.map_view = QWebEngineView()
        self.map_view.setMinimumHeight(300)

        if not path:
            # Центрування на Україну, коли маршрут не задано
            js_points = "[[48.3794, 31.1656]]"
            zoom_level = 6
            markers_code = ""
            polyline_code = ""
        else:
            city_coords = self.builder.builder.city_coords
            js_points = ",\n".join([f"[{city_coords[city][0]}, {city_coords[city][1]}]" for city in path])
            js_points = f"[{js_points}]"
            zoom_level = 5
            markers_code = "\n".join([f"L.marker(points[{i}]).addTo(map).bindPopup('Місто {i+1}');" for i in range(len(path))])
            polyline_code = "var polyline = L.polyline(points, {color: 'cyan'}).addTo(map); map.fitBounds(polyline.getBounds());"

        html_map = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Маршрут</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                html, body {{ height: 100%; margin: 0; }}
                #map {{ width: 100%; height: 100%; }}
            </style>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
            <script>
                var points = {js_points};
                var map = L.map('map').setView(points[0], {zoom_level});
                L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 18,
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);
                {markers_code}
                {polyline_code}
            </script>
        </body>
        </html>"""

        self.map_view.setHtml(html_map)
        map_layout.addWidget(close_button)
        map_layout.addWidget(self.map_view)
        self.content_layout.addWidget(self.map_container, 2, 0, 1, 5)


    def close_map(self):
        if hasattr(self, 'map_container'):
            self.content_layout.removeWidget(self.map_container)
            self.map_container.deleteLater()
            del self.map_container
            if hasattr(self, 'map_view'):
                del self.map_view

    def resizeEvent(self, event):
        self.background_label.resize(self.size())
        self.content_widget.resize(self.size())
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    db = Database(HOST, USER, PASSWORD, DATABASE)
    db.create_database()
    window = MyApp()
    window.showMaximized() 
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
