"""
Главное окно приложения с вкладками
"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, 
                             QMessageBox, QToolBar, QAction)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QTimer
from .routes_tab import RoutesTab
from .points_tab import PointsTab
from core.config import CURRENT_THEME  # Измененный импорт
from PyQt5.QtWidgets import QAction
from .theme_manager import theme_manager   
from utils.updater import UpdateManager

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Система формирования тарифов")
        self.resize(1100, 750)
        
        # Устанавливаем единый стиль через theme_manager
        self.setStyleSheet(theme_manager.get_global_style())
        
        # Центральный виджет - вкладки
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Убираем лишние рамки
        self.tabs.setElideMode(Qt.ElideNone)
        
        # Убираем подчеркивание у вкладок
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                text-decoration: none;
            }
            QTabBar::tab:selected {
                text-decoration: none;
            }
            QTabBar::tab:hover {
                text-decoration: none;
            }
        """)

        # Создаем вкладки
        self.points_tab = PointsTab(db)
        self.routes_tab = RoutesTab(db)
        
        self.tabs.addTab(self.points_tab, "Пункты")
        self.tabs.addTab(self.routes_tab, "Маршруты")
        self.setCentralWidget(self.tabs)
        
        # Статусная строка
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Панель инструментов
        self._create_toolbar()
        
        # Инициализация менеджера обновлений
        self.updater = UpdateManager(self, current_version="1.0.0")
        
        # Проверка обновлений при запуске (тихо)
        QTimer.singleShot(3000, lambda: self.updater.check_for_updates(silent=True))
    
    def _create_toolbar(self):
        toolbar = QToolBar("Основные действия")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Кнопка обновить
        refresh_action = QAction("🔄 Обновить", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._refresh_current_tab)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Кнопка настроек БД
        settings_action = QAction("⚙️ Настройки БД", self)
        settings_action.triggered.connect(self._open_settings)
        toolbar.addAction(settings_action)
        
        # Кнопка смены темы
        theme_action = QAction("🎨 Сменить тему", self)
        theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(theme_action)
        
        # Кнопка проверки обновлений
        update_action = QAction("🔄 Проверить обновления", self)
        update_action.triggered.connect(lambda: self.updater.check_for_updates(silent=False))
        toolbar.addAction(update_action)
        
        toolbar.addSeparator()

        # Добавить горячие клавиши для вкладок
        switch_to_points = QAction("Пункты", self)
        switch_to_points.setShortcut("Ctrl+1")
        switch_to_points.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        self.addAction(switch_to_points)
        
        switch_to_routes = QAction("Маршруты", self)
        switch_to_routes.setShortcut("Ctrl+2")
        switch_to_routes.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        self.addAction(switch_to_routes)
        
        # Добавить горячие клавиши для действий
        new_route = QAction("Новый маршрут", self)
        new_route.setShortcut("Ctrl+N")
        new_route.triggered.connect(lambda: self.routes_tab._add_grid())
        self.addAction(new_route)
        
        new_point = QAction("Новый пункт", self)
        new_point.setShortcut("Ctrl+Shift+N")
        new_point.triggered.connect(lambda: self.points_tab._add_point())
        self.addAction(new_point)
        
        find_shortcut = QAction("Поиск", self)
        find_shortcut.setShortcut("Ctrl+F")
        find_shortcut.triggered.connect(lambda: self._focus_search())
        self.addAction(find_shortcut)

    def _focus_search(self):
        """Фокус на поле поиска текущей вкладки"""
        current = self.tabs.currentWidget()
        if hasattr(current, 'search_input'):
            current.search_input.setFocus()
            current.search_input.selectAll()

    def _open_settings(self):
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_():
            QMessageBox.information(self, "Внимание", 
                "Настройки сохранены. Перезапустите приложение для применения изменений.")
        
    def _refresh_current_tab(self):
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
            self.statusBar.showMessage("Данные обновлены", 3000)
    
    def show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)
        self.statusBar.showMessage(f"Ошибка: {message}", 5000)
    
    def show_success(self, message: str):
        QMessageBox.information(self, "Успешно", message)
        self.statusBar.showMessage(message, 3000)
        
    def _toggle_theme(self):
        """Переключить тему оформления"""
        theme_manager.toggle_theme()
        self.setStyleSheet(theme_manager.get_global_style())
        
        # Обновляем тему во всех вкладках
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, 'update_theme'):
                widget.update_theme()
        
        self.statusBar.showMessage("Тема изменена", 3000)