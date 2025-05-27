from google import genai
from config import GEMINI_API
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyQt5.QtWidgets import QWidget,QLineEdit, QLabel, QPushButton, QVBoxLayout, QSlider, QTextEdit, QMessageBox, QCheckBox, QComboBox, QApplication,QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys


class TravelAssistant:
    def __init__(self, name, destination, style, days, save_pdf=False, language="Українська"):
        self.client = genai.Client(api_key=GEMINI_API)
        self.name = name
        self.destination = destination
        self.style = style
        self.days = days
        self.save_pdf = save_pdf
        self.language = language
        self.save_to_pdf_path = None


    def generate_recommendations(self):
        prompt = (
            f"You are a caring and knowledgeable travel planning assistant with an outgoing and funny personality. "
            f"My name is {self.name}. I am planning to travel to {self.destination} in {self.style} style "
            f"for {self.days} days. "
            f"Write the response in {self.language} language. "
            f"Describe what to do each day in detail and give some advices."
        )

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        plan_text = response.text

        if self.save_pdf:
            self.save_to_pdf(plan_text)

        return plan_text

    def save_to_pdf(self, text):
        filename = self.save_to_pdf_path if self.save_to_pdf_path else f"travel_plan_{self.name}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        c.setFont("DejaVuSans", 12)

        left_margin = 40
        right_margin = 40
        top_margin = 40
        bottom_margin = 40
        line_height = 18
        max_width = width - left_margin - right_margin

        text_object = c.beginText(left_margin, height - top_margin)
        text_object.setFont("DejaVuSans", 12)

        for paragraph in text.split('\n'):
            words = paragraph.split()
            line = ""

            for word in words:
                test_line = line + " " + word if line else word
                if pdfmetrics.stringWidth(test_line, "DejaVuSans", 12) < max_width:
                    line = test_line
                else:
                    if text_object.getY() <= bottom_margin:
                        c.drawText(text_object)
                        c.showPage()
                        c.setFont("DejaVuSans", 12)
                        text_object = c.beginText(left_margin, height - top_margin)
                        text_object.setFont("DejaVuSans", 12)
                    text_object.textLine(line)
                    line = word

            if line:
                if text_object.getY() <= bottom_margin:
                    c.drawText(text_object)
                    c.showPage()
                    c.setFont("DejaVuSans", 12)
                    text_object = c.beginText(left_margin, height - top_margin)
                    text_object.setFont("DejaVuSans", 12)
                text_object.textLine(line)

            text_object.textLine("")

        c.drawText(text_object)
        c.save()
        print(f"Your travel plan has been saved to {filename}")
        return filename


class AssistantWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initwindow()
        self.initUI()

    def initwindow(self):
        self.setWindowTitle("Скласти план відпочинку")
        self.setGeometry(800, 300, 500, 700)
        self.setStyleSheet("background-color: #f4ecd8;")
        self.setWindowIcon(QIcon("assets/LOGO.jpg"))
        

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        self.pdf_save_path = None
        field_style = """
            QLineEdit {
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
        """
        btn_style = """
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

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введіть ім'я")
        self.name_input.setStyleSheet(field_style)

        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Введіть місто для відпочинку")
        self.dest_input.setStyleSheet(field_style)

        self.style_input = QLineEdit()
        self.style_input.setPlaceholderText("Стиль відпочинку")
        self.style_input.setStyleSheet(field_style)

        self.days_label = QLabel("Days: 1", self)
        self.days_label.setAlignment(Qt.AlignCenter)

        self.days_slider = QSlider(Qt.Horizontal, self)
        self.days_slider.setMinimum(1)
        self.days_slider.setMaximum(30)
        self.days_slider.setValue(1)
        self.days_slider.setTickInterval(1)
        self.days_slider.setTickPosition(QSlider.TicksBelow)
        self.days_slider.valueChanged.connect(self.update_label)

        self.language_selector = QComboBox()
        self.language_selector.addItems(["Українська", "English"])
        self.language_selector.setStyleSheet(field_style)

        self.save_pdf_checkbox = QCheckBox("Завантажити PDF версію")


        self.file_exploler_btn = QPushButton("Вибрати шлях для Завантаження PDF")
        self.file_exploler_btn.setStyleSheet(btn_style)
        self.file_exploler_btn.clicked.connect(self.open_explorer)

        self.plan_output = QTextEdit()
        self.plan_output.setReadOnly(True)

        self.generate_button = QPushButton("Створити план")
        self.generate_button.setStyleSheet(btn_style)
        self.generate_button.clicked.connect(self.generate_plan)

        self.close_button = QPushButton("Закрити")
        self.close_button.setStyleSheet("background-color: #a94442; color: white; font-size: 14px; padding: 8px; border-radius: 6px;")
        self.close_button.clicked.connect(self.close)

        layout.addWidget(self.name_input)
        layout.addWidget(self.dest_input)
        layout.addWidget(self.style_input)
        layout.addWidget(self.days_label)
        layout.addWidget(self.days_slider)
        layout.addWidget(self.language_selector)
        layout.addWidget(self.save_pdf_checkbox)
        layout.addWidget(self.file_exploler_btn)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.plan_output)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def update_label(self, value):
        self.days_label.setText(f"Days: {value}")
    def open_explorer(self):
        directory = QFileDialog.getExistingDirectory(self, "Оберіть папку для збереження PDF")
        if directory:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Увага", "Спочатку введіть ім’я!")
                return
            filename = f"travel_plan_{name}.pdf"
            self.pdf_save_path = f"{directory}/{filename}"
            QMessageBox.information(self, "Шлях обрано", f"PDF буде збережено в:\n{self.pdf_save_path}")


    def generate_plan(self):
        name = self.name_input.text()
        destination = self.dest_input.text()
        style = self.style_input.text()
        days = str(self.days_slider.value())
        save_pdf = self.save_pdf_checkbox.isChecked()
        language = self.language_selector.currentText()

        if name and destination and style:
                    assistant = TravelAssistant(
            name, destination, style, days, save_pdf, language
        )
        if self.pdf_save_path:
            assistant.save_to_pdf_path = self.pdf_save_path
            plan = assistant.generate_recommendations()
            self.plan_output.setPlainText(plan)

            if save_pdf:
                QMessageBox.information(self, "Файл збережено", f"Ваш план відпочинку збережено у файл travel_plan_{name}.pdf")
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть усі поля!")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.showMaximized() 
    window.show()
    sys.exit(app.exec_())
