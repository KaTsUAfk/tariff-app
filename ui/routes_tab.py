"""
Вкладка управления тарифными сетками
"""
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QMenu, QHeaderView
from PyQt5.QtCore import Qt, QPoint

from .base_tab import BaseTab
from .table_mixin import TableMixin
from .widgets import SearchBox, Button
from .route_edit_dialog import RouteEditDialog
from .route_grid_dialog import EnhancedRouteGridDialog

class RoutesTab(BaseTab, TableMixin):
    def __init__(self, db):
        super().__init__(db)
        self.grids = []
        self.table_columns = ["ID", "№ маршрута", "Название"]
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Поиск и добавление
        top_layout = QHBoxLayout()
        self.search_input = SearchBox("Поиск маршрута по номеру или названию...")
        self.search_input.textChanged.connect(self._on_search)
        top_layout.addWidget(self.search_input)
        
        self.add_btn = Button("➕ Добавить маршрут", primary=True)
        self.add_btn.clicked.connect(self._add_grid)
        top_layout.addWidget(self.add_btn)
        
        self.delete_btn = Button("❌ Удалить маршрут")
        self.delete_btn.clicked.connect(self._delete_grid)
        top_layout.addWidget(self.delete_btn)
        
        layout.addLayout(top_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.setup_table_style(self.table, self.table_columns)
        
        # Скрываем колонку с ID
        self.table.setColumnHidden(0, True)
        
        # Настраиваем ширину колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (скрыта)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # № маршрута
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Название (растягивается)
        
        # Устанавливаем минимальную ширину для колонки с номером
        self.table.setColumnWidth(1, 100)  # Ширина для номера маршрута
        
        # Включаем контекстное меню и двойной клик
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._open_grid_editor)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def _show_context_menu(self, pos: QPoint):
        """Показать контекстное меню"""
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        
        self.table.selectRow(index.row())
        
        data = self.get_selected_row_data(self.table, ['id', 'number', 'name'])
        if not data:
            return
        
        route_id = int(data['id'])
        route_number = data['number']
        route_name = data['name']
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Редактировать маршрут")
        edit_action.triggered.connect(lambda: self._edit_route(route_id))
        
        duplicate_action = menu.addAction("📋 Дублировать маршрут")
        duplicate_action.triggered.connect(lambda: self._duplicate_route(route_id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("❌ Удалить маршрут")
        delete_action.triggered.connect(lambda: self._delete_route(route_id, route_number, route_name))
        
        menu.exec_(self.table.viewport().mapToGlobal(pos))
    
    def _edit_route(self, route_id: int):
        """Редактировать маршрут"""
        dialog = RouteEditDialog(self.db, route_id, parent=self)
        if dialog.exec_():
            self.load_data()
    
    def _duplicate_route(self, source_route_id: int):
        """Дублировать маршрут"""
        try:
            source_route = self.db.get_route_by_id(source_route_id)
            if not source_route:
                self.show_error("Ошибка", "Исходный маршрут не найден")
                return
            
            source_sequence = self.db.get_route_sequence(source_route_id)
            
            new_number = f"Копия {source_route['route_number']}"
            new_name = source_route['route_name']
            
            new_route_id = self.db.add_route(new_number, new_name)
            
            for point in source_sequence:
                self.db.add_point_to_route(
                    new_route_id,
                    point['point_id'],
                    point['distance_km'],
                    point['rounding'],
                    point['cost_per_km'],
                    point['baggage_percent']
                )
            
            self.show_info("Успешно", f"Маршрут продублирован\nНовый маршрут: {new_number} — {new_name}")
            self.load_data()
            
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось дублировать маршрут: {str(e)}")
    
    def _delete_route(self, route_id: int, route_number: str, route_name: str):
        """Удалить маршрут"""
        if not self.show_question("Подтверждение", 
            f"Удалить маршрут №{route_number} — {route_name}?"):
            return
        
        try:
            self.db.delete_route(route_id)
            self.load_data()
            self.show_info("Успешно", "Маршрут удалён")
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось удалить маршрут: {e}")
    
    def load_data(self, grids=None):
        if grids is None:
            try:
                grids = self.db.get_all_routes()
            except Exception as e:
                self.show_error("Ошибка", f"Не удалось загрузить маршруты: {e}")
                return
        
        self.grids = grids
        self.table.setRowCount(len(grids))
        for row, grid in enumerate(grids):
            # ID (скрытая колонка)
            self.table.setItem(row, 0, self.create_item(str(grid['id'])))
            
            # № маршрута - форматируем как строку, чтобы сохранить ведущие нули если есть
            route_number = grid['route_number']
            self.table.setItem(row, 1, self.create_item(route_number))
            
            # Название маршрута
            self.table.setItem(row, 2, self.create_item(grid['route_name']))
    
    def _on_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.load_data()
            return
        
        try:
            all_routes = self.db.get_all_routes()
            filtered = [
                r for r in all_routes 
                if query in r['route_number'].lower() or query in r['route_name'].lower()
            ]
            self.load_data(filtered)
        except Exception as e:
            self.show_error("Ошибка", f"Ошибка поиска: {e}")
    
    def _get_selected_grid_id(self):
        data = self.get_selected_row_data(self.table, ['id'])
        if not data:
            self.show_warning("Внимание", "Выберите маршрут из списка")
            return None
        return int(data['id'])
    
    def _add_grid(self):
        dialog = RouteEditDialog(self.db, parent=self)
        if dialog.exec_():
            self.load_data()
    
    def _delete_grid(self):
        grid_id = self._get_selected_grid_id()
        if grid_id is None:
            return
        
        row = self.table.currentRow()
        route_number = self.table.item(row, 1).text()
        route_name = self.table.item(row, 2).text()
        
        self._delete_route(grid_id, route_number, route_name)
    
    def _open_grid_editor(self, index):
        route_id = int(self.table.item(index.row(), 0).text())
        route_number = self.table.item(index.row(), 1).text()
        route_name = self.table.item(index.row(), 2).text()
        
        dialog = EnhancedRouteGridDialog(self.db, route_id, route_number, route_name, parent=self)
        dialog.exec_()
        self.load_data()
    
    def update_theme(self):
        """Обновить тему вкладки маршрутов"""
        # Обновляем стиль таблицы
        self._apply_table_theme(self.table)
        
        # Обновляем стиль поля поиска
        if hasattr(self, 'search_input'):
            self.search_input.update_theme()
        
        # Обновляем стили кнопок
        for btn in [self.add_btn, self.delete_btn]:
            if hasattr(btn, 'update_theme'):
                btn.update_theme()
                