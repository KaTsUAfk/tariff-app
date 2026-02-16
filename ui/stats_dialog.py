"""Диалог статистики"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from .base_dialog import BaseDialog

class StatsDialog(BaseDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Статистика")
        self.resize(600, 400)
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Общая статистика
        stats_layout = QHBoxLayout()
        
        self.points_label = QLabel("Пунктов: 0")
        self.points_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.points_label)
        
        self.routes_label = QLabel("Маршрутов: 0")
        self.routes_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.routes_label)
        
        self.total_points_label = QLabel("Всего остановок: 0")
        self.total_points_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.total_points_label)
        
        layout.addLayout(stats_layout)
        
        # Таблица маршрутов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Маршрут", "Кол-во пунктов", "Общее расстояние", "Стоимость"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Кнопка обновить
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_stats)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_stats(self):
        """Загрузить статистику"""
        try:
            # Общая статистика
            points = self.db.get_all_points()
            routes = self.db.get_all_routes()
            
            self.points_label.setText(f"Пунктов: {len(points)}")
            self.routes_label.setText(f"Маршрутов: {len(routes)}")
            
            total_stops = 0
            self.table.setRowCount(len(routes))
            
            for i, route in enumerate(routes):
                sequence = self.db.get_route_sequence(route['id'])
                total_stops += len(sequence)
                
                # Расчет общего расстояния
                total_distance = 0
                if len(sequence) > 1:
                    total_distance = sequence[-1]['distance_km']
                
                # Примерная стоимость
                cost = 0
                if sequence:
                    cost = total_distance * float(sequence[0]['cost_per_km'])
                
                self.table.setItem(i, 0, QTableWidgetItem(f"{route['route_number']} — {route['route_name']}"))
                self.table.setItem(i, 1, QTableWidgetItem(str(len(sequence))))
                self.table.setItem(i, 2, QTableWidgetItem(f"{total_distance:.1f} км"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{cost:.2f} ₽"))
            
            self.total_points_label.setText(f"Всего остановок: {total_stops}")
            
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось загрузить статистику: {e}")