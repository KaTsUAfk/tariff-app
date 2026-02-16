"""
Миксин с общими методами для работы с таблицами
"""
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .theme_manager import theme_manager

class TableMixin:
    """Миксин с методами для работы с таблицами"""
    
    def setup_table_style(self, table, columns):
        """Настройка стиля таблицы"""
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(False)  # Отключаем стандартное чередование цветов
        
        # Включаем сортировку
        table.setSortingEnabled(True)
        
        # Убираем пунктирную обводку
        table.setFocusPolicy(Qt.NoFocus)
        
        # Применяем стиль из темы с поддержкой чередования цветов
        self._apply_table_theme(table)
    
        # Включить сортировку
        table.setSortingEnabled(True)
        
        # Разрешить перемещение колонок
        table.horizontalHeader().setSectionsMovable(True)
        
        # Сохранять состояние колонок
        table.horizontalHeader().setStretchLastSection(True)
    
    def _apply_table_theme(self, table):
        """Применить тему к таблице с поддержкой чередования цветов"""
        # Получаем цвета из темы
        bg_color = theme_manager.current_theme['panel_bg']
        text_color = theme_manager.current_theme['text']
        border_color = theme_manager.current_theme['border']
        selection_color = theme_manager.current_theme['accent']
        hover_color = theme_manager.current_theme['selection']
        
        # Определяем, какая тема сейчас активна по цвету текста
        is_light_theme = (text_color != '#ffffff')
        
        # Создаем цвета для таблицы в зависимости от темы
        if is_light_theme:
            # Для светлой темы - заголовки БЕЛЫЕ, фон таблицы тёплый
            alternate_bg = "#eae4d8"     # Тёплый светло-бежевый для четных строк
            header_bg = "#ffffff"        # БЕЛЫЙ для заголовков
            header_text = "#2c2c2c"      # Тёмный текст для заголовков
            grid_color = "#d6cec0"       # Тёплый цвет сетки
            corner_bg = "#ffffff"        # БЕЛЫЙ для уголка
        else:
            # Для темной темы
            alternate_bg = "#2d2d2d"     # Чуть светлее темного для четных строк
            header_bg = "#404040"        # Темно-серый для заголовков
            header_text = "#ffffff"       # Белый текст для заголовков
            grid_color = border_color     # Цвет сетки как границы
            corner_bg = "#404040"         # Темно-серый для уголка
        
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_color};
                color: {text_color};
                gridline-color: {grid_color};
                outline: none;
                alternate-background-color: {alternate_bg};
                border: none;  /* Убираем внешнюю границу таблицы */
            }}
            QTableWidget::item {{
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 4px;
                padding-bottom: 4px;
                border: none;
                outline: none;
                color: {text_color};
            }}
            QTableWidget::item:alternate {{
                background-color: {alternate_bg};
                color: {text_color};
            }}
            QTableWidget::item:hover {{
                background-color: {hover_color};
                color: {text_color};
            }}
            QTableWidget::item:selected {{
                background-color: {selection_color};
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                border: 1px solid {border_color};
                padding: 4px;
                font-weight: bold;
            }}
            QTableCornerButton::section {{
                background-color: {corner_bg};
                border: none;  /* Убираем границы у уголка */
            }}
        """)
    
    def setup_large_table(self, table):
        """Настройка таблицы для работы с большими данными"""
        table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        
        # Оптимизация для большого количества строк
        table.setUpdatesEnabled(False)
        table.setupViewport()
        table.setUpdatesEnabled(True)

    def setup_large_table(self, table):
        """Настройка таблицы для работы с большими данными"""
        table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        
        # Оптимизация для большого количества строк
        table.setUpdatesEnabled(False)
        table.setupViewport()
        table.setUpdatesEnabled(True)
        
        # Кэширование данных
        table.setAutoScroll(True)
        table.setAutoScrollMargin(16)

    def create_item(self, text, alignment=Qt.AlignLeft | Qt.AlignVCenter, 
                   editable=False, tooltip=""):
        """Создать элемент таблицы"""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(alignment)
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        if tooltip:
            item.setToolTip(tooltip)
        return item
    
    def highlight_row(self, table, row, color=None):
        """Подсветить строку таблицы"""
        if color is None:
            # Используем цвет выделения из темы
            color = QColor(theme_manager.current_theme['selection'])
        
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(color)
    
    def get_selected_row_data(self, table, columns):
        """Получить данные выбранной строки"""
        selected = table.selectionModel().selectedRows()
        if not selected:
            return None
        
        row = selected[0].row()
        data = {}
        for col, key in enumerate(columns):
            item = table.item(row, col)
            data[key] = item.text() if item else ""
        return data
    
    def clear_table(self, table):
        """Очистить таблицу"""
        table.clearContents()
        table.setRowCount(0)
    
    def update_theme(self):
        """Обновить тему для таблиц (вызывается при смене темы)"""
        if hasattr(self, 'table'):
            self._apply_table_theme(self.table)