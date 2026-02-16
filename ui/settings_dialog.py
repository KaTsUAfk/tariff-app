from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
import json
from pathlib import Path
import sys
from core.config import save_config, load_config  # Измененный импорт

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки подключения к БД")
        self.setModal(True)
        self.resize(400, 250)
        
        # Определяем путь к конфигу
        if getattr(sys, 'frozen', False):
            self.config_path = Path(sys.executable).parent / 'config.json'
        else:
            self.config_path = Path(__file__).parent.parent / 'config.json'
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        form_layout.addRow("Хост:", self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        form_layout.addRow("Порт:", self.port_input)
        
        self.dbname_input = QLineEdit()
        form_layout.addRow("База данных:", self.dbname_input)
        
        self.user_input = QLineEdit()
        form_layout.addRow("Пользователь:", self.user_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_config)
        test_btn = QPushButton("🔌 Проверить подключение")
        test_btn.clicked.connect(self.test_connection)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_config(self):
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    db_config = config.get('database', {})
                    
                    self.host_input.setText(db_config.get('host', 'localhost'))
                    self.port_input.setValue(db_config.get('port', 5432))
                    self.dbname_input.setText(db_config.get('dbname', 'tariffs_db'))
                    self.user_input.setText(db_config.get('user', 'postgres'))
                    self.password_input.setText(db_config.get('password', '12345678'))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить конфиг: {e}")
    
    def save_config(self):
        config = {
            "database": {
                "host": self.host_input.text(),
                "port": self.port_input.value(),
                "dbname": self.dbname_input.text(),
                "user": self.user_input.text(),
                "password": self.password_input.text()
            },
            "theme": "light"
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Успешно", "Настройки сохранены")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфиг: {e}")
    
    def test_connection(self):
        import psycopg2
        try:
            conn = psycopg2.connect(
                host=self.host_input.text(),
                port=self.port_input.value(),
                dbname=self.dbname_input.text(),
                user=self.user_input.text(),
                password=self.password_input.text(),
                client_encoding='UTF8'  # ЯВНО УКАЗЫВАЕМ КОДИРОВКУ!
            )
            conn.close()
            QMessageBox.information(self, "Успешно", "Подключение к БД установлено!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться: {e}")