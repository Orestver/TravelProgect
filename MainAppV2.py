import sys,os,re
import mysql.connector
from mysql.connector import Error


from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QGridLayout, QLineEdit, QMessageBox, QVBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import  QFont, QPixmap, QIcon
import sys,os

from config import HOST,USER,PASSWORD,DATABASE


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
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
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
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                print(f"👋 Вітаємо, {user[0]}! Вхід успішний.")
                return True, user[0]
            else:
                print("❌ Невірний email або пароль.")
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
        self.init_window()
        self.init_UI()
        self.is_autorized = False
        

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
        self.reg_button.clicked.connect(self.open_register_window)
        self.reg_button.setEnabled(True)

        self.log_button = QPushButton("Авторизуватися")
        self.log_button.setStyleSheet(self.btn_style())
        self.log_button.clicked.connect(self.open_login_window)
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
        
    def open_login_window(self):
        self.log_db = Login_window()
        self.log_db.setAttribute(Qt.WA_DeleteOnClose)
        self.log_db.login_successful.connect(self.on_authenticated)
        self.log_db.show()
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
    db = Database(HOST, USER, PASSWORD, DATABASE)
    db.create_database()
    window.showMaximized() 
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
