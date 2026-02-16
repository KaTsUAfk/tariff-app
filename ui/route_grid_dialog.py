"""
Диалог редактирования маршрута с расчётом тарифов (пассажирский + багаж)
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox, 
                             QComboBox, QHeaderView, QLabel, QWidget, 
                             QAbstractItemView, QTextEdit, QCheckBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QRegExpValidator
from PyQt5.QtCore import QRegExp

from .export_import_mixin import ExportImportMixin
from .validation_mixin import ValidationMixin
from .point_dialog import PointAddDialog
from .services import PointService
from .constants import TABLE_HEADERS, REGEX
from .theme_manager import theme_manager
from PyQt5.QtCore import QTimer

class RouteGridDialog(QDialog, ExportImportMixin, ValidationMixin):
    def __init__(self, db, route_id, route_number, route_name, parent=None):
        super().__init__(parent)
        self.db = db
        self.point_service = PointService(db)
        self.route_id = route_id
        self.route_number = route_number
        self.route_name = route_name
        self.original_data = []
        
        self.setWindowTitle(f"Маршрут №{route_number} — {route_name}")
        self.setModal(True)
        self.resize(1100, 650)
        
        # Применяем стиль из темы
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme_manager.current_theme['window_bg']};
                color: {theme_manager.current_theme['text']};
            }}
            QLabel {{
                color: {theme_manager.current_theme['text']};
            }}
            QCheckBox {{
                color: {theme_manager.current_theme['text']};
            }}
        """)
        
        try:
            self.route_info = db.get_route_by_id(route_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные маршрута: {e}")
            self.reject()
            return
        
        self.setup_ui()
        self.load_points()
        self.load_route_sequence()
    
    def _get_global_parameters(self):
        """Получить глобальные параметры маршрута из первого пункта"""
        try:
            if hasattr(self, 'sequence_table') and self.sequence_table.rowCount() > 0:
                first_row = 0
                global_rounding = float(self.sequence_table.item(first_row, 3).text())
                global_cost_per_km = float(self.sequence_table.item(first_row, 4).text())
                global_baggage_percent = float(self.sequence_table.item(first_row, 5).text())
                
                return {
                    'rounding': global_rounding,
                    'cost_per_km': global_cost_per_km,
                    'baggage_percent': global_baggage_percent
                }
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Ошибка получения глобальных параметров: {e}")
        
        # Значения по умолчанию
        return {
            'rounding': 0.0,
            'cost_per_km': 10.0,
            'baggage_percent': 0.0
        }
    
    def _get_or_create_point(self, point_name, all_points):
        """Получить ID существующего пункта или создать новый"""
        point_name_lower = point_name.lower()
        if point_name_lower in all_points:
            return all_points[point_name_lower]
        
        try:
            point_id = self.db.add_point(point_name)
            all_points[point_name_lower] = point_id
            return point_id
        except Exception as e:
            print(f"Ошибка создания пункта '{point_name}': {e}")
            return None
    
    def _show_import_result(self, imported_count, errors):
        """Показать результат импорта"""
        if errors:
            error_text = "\n".join(errors[:5])
            if len(errors) > 5:
                error_text += f"\n... и еще {len(errors) - 5} ошибок"
            
            QMessageBox.warning(
                self, 
                "Импорт завершен с ошибками",
                f"Успешно импортировано: {imported_count}\n"
                f"Ошибок: {len(errors)}\n\n"
                f"Первые ошибки:\n{error_text}"
            )
        else:
            QMessageBox.information(
                self,
                "Импорт успешен",
                f"Успешно импортировано {imported_count} пунктов"
            )
    
    def _create_button(self, text, button_type="default", icon=None):
        """Создать кнопку с применением темы"""
        btn = QPushButton(text)
        if icon:
            btn.setText(f"{icon} {text}")
        btn.setStyleSheet(theme_manager.get_button_style(button_type))
        return btn
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок маршрута
        title_label = QLabel(f"<h3>Маршрут №{self.route_number} — {self.route_name}</h3>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Верхняя панель с элементами управления
        self._setup_top_panel(layout)
        
        # Таблица последовательности пунктов
        self._setup_table(layout)
        
        # Кнопки управления
        self._setup_buttons(layout)
        
        self.setLayout(layout)
    
    def _setup_top_panel(self, layout):
        """Настройка верхней панели с выбором пункта и расстоянием"""
        top_panel = QHBoxLayout()
        
        # Левая группа: выбор пункта и расстояние
        left_group = QHBoxLayout()
        left_group.addWidget(QLabel("Выбор пункта:"))
        
        self.points_combo = QComboBox()
        self.points_combo.setMinimumWidth(250)
        self.points_combo.setStyleSheet(theme_manager.get_input_style())
        left_group.addWidget(self.points_combo)
        
        # Кнопка добавления выбранного пункта в маршрут
        self.add_to_route_btn = self._create_button("➕ Добавить в маршрут", "secondary")
        self.add_to_route_btn.clicked.connect(self._add_point_to_route)
        left_group.addWidget(self.add_to_route_btn)
        
        left_group.addWidget(QLabel("Расстояние:"))
        self._setup_distance_input(left_group)
        
        top_panel.addLayout(left_group)
        top_panel.addStretch()
        
        # Правая группа: настройки округления
        right_group = self._setup_right_panel()
        top_panel.addLayout(right_group)
        
        top_widget = QWidget()
        top_widget.setLayout(top_panel)
        layout.addWidget(top_widget)
    
    def _setup_distance_input(self, parent_layout):
        """Настройка поля ввода расстояния"""
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Введите расстояние")
        self.distance_input.setAlignment(Qt.AlignRight)
        self.distance_input.setFixedWidth(120)
        self.distance_input.setStyleSheet(theme_manager.get_input_style())
        
        # Валидатор для чисел с плавающей точкой
        regex = QRegExp(REGEX['number'])
        validator = QRegExpValidator(regex)
        self.distance_input.setValidator(validator)
        
        self.distance_input.setText("0.0")
        parent_layout.addWidget(self.distance_input)
    
    def _setup_right_panel(self):
        """Настройка правой панели с округлением и кнопкой нового пункта"""
        right_group = QHBoxLayout()
        
        right_group.addWidget(QLabel("Тип округления:"))
        
        self.rounding_checkbox = QCheckBox("В бóльшую сторону")
        self.rounding_checkbox.setChecked(False)
        self.rounding_checkbox.stateChanged.connect(self._on_rounding_changed)
        right_group.addWidget(self.rounding_checkbox)
        
        right_group.addSpacing(30)
        
        # Кнопка добавления нового пункта
        self.new_point_btn = self._create_button("➕ Новый пункт", "primary")
        self.new_point_btn.clicked.connect(self._add_new_point)
        right_group.addWidget(self.new_point_btn)
        
        return right_group
    
    def _setup_table(self, layout):
        """Настройка таблицы последовательности пунктов"""
        self.sequence_table = QTableWidget()
        self.sequence_table.setColumnCount(len(TABLE_HEADERS['route_sequence']))
        self.sequence_table.setHorizontalHeaderLabels(TABLE_HEADERS['route_sequence'])
        self.sequence_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sequence_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sequence_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sequence_table.setStyleSheet(theme_manager.get_table_style())
        layout.addWidget(self.sequence_table)
    
    def _setup_buttons(self, layout):
        """Настройка кнопок управления"""
        # Первая строка кнопок
        btn_layout1 = QHBoxLayout()

        self.calc_btn = self._create_button("🧮 Рассчитать", "default")
        self.calc_btn.clicked.connect(self._calculate_preview)
        btn_layout1.addWidget(self.calc_btn)

        sort_btn = self._create_button("📊 Сортировать по расстоянию", "default")
        sort_btn.clicked.connect(self._sort_by_distance)
        btn_layout1.addWidget(sort_btn)

        self.save_btn = self._create_button("💾 Сохранить изменения", "default")
        self.save_btn.clicked.connect(self._save_changes)
        btn_layout1.addWidget(self.save_btn)

        del_btn = self._create_button("❌ Удалить пункт", "default")
        del_btn.clicked.connect(self._delete_point)
        btn_layout1.addWidget(del_btn)
        
        preview_btn = self._create_button("🖨️ Таблица стоимости", "default")
        preview_btn.clicked.connect(self._show_cost_table)
        btn_layout1.addWidget(preview_btn)

        btn_layout1.addStretch()
        close_btn = self._create_button("Закрыть", "default")
        close_btn.clicked.connect(self.accept)
        btn_layout1.addWidget(close_btn)

        # Вторая строка кнопок
        btn_layout2 = QHBoxLayout()

        export_btn = self._create_button("📤 Экспорт", "default")
        export_btn.clicked.connect(self.export_route)
        btn_layout2.addWidget(export_btn)
        
        import_btn = self._create_button("📥 Импорт", "default")
        import_btn.clicked.connect(self.import_from_file)
        btn_layout2.addWidget(import_btn)

        validate_btn = self._create_button("✓ Проверить данные", "default")
        validate_btn.clicked.connect(self._validate_and_show)
        btn_layout2.addWidget(validate_btn)

        btn_layout2.addStretch()

        layout.addLayout(btn_layout1)
        layout.addLayout(btn_layout2)
    
    def _add_new_point(self):
        """Диалог добавления нового пункта назначения в базу данных"""
        dialog = PointAddDialog(self.db, self)
        if dialog.exec_():
            point_id = dialog.get_point_id()
            self.load_points()
            
            index = self.points_combo.findData(point_id)
            if index >= 0:
                self.points_combo.setCurrentIndex(index)
    
    def _sort_by_distance(self):
        """Сортировка пунктов по расстоянию"""
        try:
            rows = self.sequence_table.rowCount()
            if rows <= 1:
                QMessageBox.information(self, "Информация", "Недостаточно пунктов для сортировки")
                return
            
            data = []
            for row in range(rows):
                point_name = self.sequence_table.item(row, 1).text()
                distance = float(self.sequence_table.item(row, 2).text())
                rounding = float(self.sequence_table.item(row, 3).text())
                cost = float(self.sequence_table.item(row, 4).text())
                baggage = float(self.sequence_table.item(row, 5).text())
                passenger = self.sequence_table.item(row, 6).text()
                baggage_tariff = self.sequence_table.item(row, 7).text()
                
                # Находим соответствующий ID
                seq_id = None
                for orig in self.original_data:
                    if (orig['point_name'] == point_name and 
                        abs(orig['distance_km'] - distance) < 0.1):
                        seq_id = orig['id']
                        break
                
                data.append({
                    'id': seq_id,
                    'point_name': point_name,
                    'distance': distance,
                    'rounding': rounding,
                    'cost': cost,
                    'baggage': baggage,
                    'passenger': passenger,
                    'baggage_tariff': baggage_tariff
                })
            
            # Сортировка по расстоянию
            data.sort(key=lambda x: x['distance'])
            
            # Обновляем параметры в БД
            for item in data:
                if item['id']:
                    for orig in self.original_data:
                        if orig['id'] == item['id']:
                            if (abs(orig['distance_km'] - item['distance']) > 0.01 or
                                abs(orig['rounding'] - item['rounding']) > 0.01 or
                                abs(orig['cost_per_km'] - item['cost']) > 0.01 or
                                abs(orig['baggage_percent'] - item['baggage']) > 0.01):
                                
                                self.db.update_route_point(
                                    item['id'], item['distance'],
                                    item['rounding'], item['cost'], item['baggage']
                                )
                            break
            
            # Обновляем порядок
            new_order_ids = [d['id'] for d in data if d['id']]
            if new_order_ids:
                self.db.reorder_route_sequence(self.route_id, new_order_ids)
            
            # Обновляем данные
            self.original_data = self.db.get_route_sequence(self.route_id)
            self._refresh_table(data)
            self._calculate_preview()
            
            QMessageBox.information(self, "Сортировка выполнена", 
                "Пункты отсортированы по возрастанию расстояния.\nПорядок сохранён в базе данных.")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить сортировку: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _refresh_table(self, data):
        """Обновить таблицу с данными"""
        self.sequence_table.setUpdatesEnabled(False)
        try:
            self.sequence_table.setRowCount(len(data))
            for row, d in enumerate(data):
                # № п/п (нередактируемый)
                self.sequence_table.setItem(row, 0, self._create_item(str(row + 1), align=Qt.AlignCenter, editable=False))
                
                # Пункт назначения (РЕДАКТИРУЕМЫЙ)
                point_item = self._create_item(d['point_name'], align=Qt.AlignLeft | Qt.AlignVCenter, editable=True)
                point_item.setToolTip("Название пункта")
                self.sequence_table.setItem(row, 1, point_item)
                
                # Расстояние (РЕДАКТИРУЕМЫЙ)
                dist_item = self._create_item(f"{d['distance']:.1f}", align=Qt.AlignRight | Qt.AlignVCenter, editable=True)
                if row == 0 and abs(d['distance']) < 0.01:
                    dist_item.setToolTip("Первый пункт - расстояние всегда 0 км")
                    dist_item.setFlags(dist_item.flags() & ~Qt.ItemIsEditable)  # Первый пункт нередактируемый
                else:
                    dist_item.setToolTip("Расстояние от начала маршрута")
                self.sequence_table.setItem(row, 2, dist_item)
                
                # Округление (РЕДАКТИРУЕМЫЙ только для первого пункта)
                rounding_item = self._create_item(f"{d['rounding']:.1f}", align=Qt.AlignRight | Qt.AlignVCenter, editable=(row == 0))
                if row == 0:
                    rounding_item.setToolTip("Округление для ВСЕГО маршрута")
                else:
                    rounding_item.setToolTip("Округление наследуется от первого пункта")
                self.sequence_table.setItem(row, 3, rounding_item)
                
                # Стоимость за км (РЕДАКТИРУЕМЫЙ только для первого пункта)
                cost_item = self._create_item(f"{d['cost']:.2f}", align=Qt.AlignRight | Qt.AlignVCenter, editable=(row == 0))
                if row == 0:
                    cost_item.setToolTip("Стоимость за км для ВСЕГО маршрута")
                else:
                    cost_item.setToolTip("Стоимость наследуется от первого пункта")
                self.sequence_table.setItem(row, 4, cost_item)
                
                # Багаж % (РЕДАКТИРУЕМЫЙ только для первого пункта)
                baggage_item = self._create_item(f"{d['baggage']:.1f}", align=Qt.AlignRight | Qt.AlignVCenter, editable=(row == 0))
                if row == 0:
                    baggage_item.setToolTip("Процент багажа для ВСЕГО маршрута")
                else:
                    baggage_item.setToolTip("Процент багажа наследуется от первого пункта")
                self.sequence_table.setItem(row, 5, baggage_item)
                
                # Тарифы (нередактируемые)
                passenger_item = self._create_item(d['passenger'], align=Qt.AlignRight | Qt.AlignVCenter,
                                                bold=True, editable=False)
                self.sequence_table.setItem(row, 6, passenger_item)
                
                baggage_tariff_item = self._create_item(d['baggage_tariff'], align=Qt.AlignRight | Qt.AlignVCenter,
                                                        editable=False)
                self.sequence_table.setItem(row, 7, baggage_tariff_item)
            
            self.sequence_table.resizeColumnsToContents()
        finally:
            self.sequence_table.setUpdatesEnabled(True)

    def _create_item(self, text, align=Qt.AlignLeft | Qt.AlignVCenter, 
                    bold=False, editable=False, tooltip=""):
        """Создать элемент таблицы"""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if bold:
            item.setFont(QFont("Arial", 9, QFont.Bold))
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        if tooltip:
            item.setToolTip(tooltip)
        return item
    
    def _on_rounding_changed(self):
        """Обработчик изменения типа округления"""
        self._calculate_preview()
    
    def load_points(self):
        """Загрузка доступных пунктов"""
        try:
            all_points = self.point_service.get_all_points()
            route_points = self.db.get_route_sequence(self.route_id)
            used_point_ids = {rp['point_id'] for rp in route_points}
            
            self.points_combo.clear()
            for point in all_points:
                if point['id'] not in used_point_ids:
                    self.points_combo.addItem(point['name'], point['id'])
            
            if self.points_combo.count() == 0:
                self.points_combo.addItem("Нет доступных пунктов", -1)
                self.points_combo.setEnabled(False)
            else:
                self.points_combo.setEnabled(True)
                
                if len(route_points) == 0:
                    self.distance_input.setEnabled(False)
                    self.distance_input.setPlaceholderText("0.0 (первый пункт)")
                    self.distance_input.setText("0.0")
                else:
                    self.distance_input.setEnabled(True)
                    self.distance_input.setPlaceholderText("Введите расстояние")
                    self.distance_input.setText("")
                    self.distance_input.setFocus()
                    self.distance_input.selectAll()
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пункты: {e}")
            self.points_combo.clear()
            self.points_combo.addItem("Ошибка загрузки", -1)
            self.points_combo.setEnabled(False)
    
    def load_route_sequence(self):
        """Загрузка последовательности пунктов маршрута"""
        try:
            points = self.db.get_route_sequence(self.route_id)
            self.sequence_table.setRowCount(len(points))
            
            self.original_data = []
            
            # Глобальные параметры из первого пункта
            global_rounding = 0.0
            global_cost_per_km = 10.0
            global_baggage_percent = 0.0
            
            if points:
                global_rounding = float(points[0]['rounding'])
                global_cost_per_km = float(points[0]['cost_per_km'])
                global_baggage_percent = float(points[0]['baggage_percent'])
            
            data = []
            for row, p in enumerate(points):
                self.original_data.append({
                    'id': p['id'],
                    'point_id': p['point_id'],
                    'point_name': p['point_name'],
                    'sequence_number': p['sequence_number'],
                    'distance_km': float(p['distance_km']),
                    'rounding': float(p['rounding']),
                    'cost_per_km': float(p['cost_per_km']),
                    'baggage_percent': float(p['baggage_percent'])
                })
                
                rounding_val = p['rounding'] if p['sequence_number'] == 1 else global_rounding
                cost_val = p['cost_per_km'] if p['sequence_number'] == 1 else global_cost_per_km
                baggage_val = p['baggage_percent'] if p['sequence_number'] == 1 else global_baggage_percent
                
                tariffs = self.db.calculate_tariffs(
                    p['distance_km'],
                    global_cost_per_km,
                    global_baggage_percent,
                    global_rounding,
                    self.rounding_checkbox.isChecked()
                )
                
                data.append({
                    'point_name': p['point_name'],
                    'distance': p['distance_km'],
                    'rounding': rounding_val,
                    'cost': cost_val,
                    'baggage': baggage_val,
                    'passenger': f"{tariffs['passenger']:.2f}",
                    'baggage_tariff': f"{tariffs['baggage']:.2f}"
                })
            
            self._refresh_table(data)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить маршрут: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_point_to_route(self):
        """Добавить пункт в маршрут"""
        point_id = self.points_combo.currentData()
        if point_id == -1 or point_id is None:
            QMessageBox.warning(self, "Внимание", "Нет доступных пунктов для добавления")
            return
        
        try:
            distance_text = self.distance_input.text().strip()
            if not distance_text:
                distance_text = "0"
            
            distance_text = distance_text.replace(',', '.')
            distance = float(distance_text)
            
            if distance < 0:
                QMessageBox.warning(self, "Ошибка", "Расстояние не может быть отрицательным")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное расстояние")
            return
        
        if self.sequence_table.rowCount() == 0:
            distance = 0.0
        
        try:
            global_rounding = 0.0
            global_cost_per_km = 10.0
            global_baggage_percent = 0.0
            
            if self.sequence_table.rowCount() > 0:
                first_row = 0
                global_rounding = float(self.sequence_table.item(first_row, 3).text())
                global_cost_per_km = float(self.sequence_table.item(first_row, 4).text())
                global_baggage_percent = float(self.sequence_table.item(first_row, 5).text())
            
            self.db.add_point_to_route(
                self.route_id, point_id, distance,
                global_rounding, global_cost_per_km, global_baggage_percent
            )
            
            QMessageBox.information(self, "Успешно", "Пункт добавлен в маршрут")
            self.load_points()
            self.load_route_sequence()
            
            self.distance_input.setText("")
            self.distance_input.setFocus()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пункт: {str(e)}")
    
    def _get_selected_sequence_id(self):
        """Получить ID выбранного пункта"""
        selected = self.sequence_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пункт из списка")
            return None
        row = selected[0].row()
        if row < len(self.original_data):
            return self.original_data[row]['id']
        return None
    
    def _delete_point(self):
        """Удалить пункт из маршрута"""
        seq_id = self._get_selected_sequence_id()
        if not seq_id:
            return
        
        row = self.sequence_table.currentRow()
        point_name = self.sequence_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить пункт '{point_name}' из маршрута?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.remove_point_from_route(seq_id)
                self.load_points()
                self.load_route_sequence()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пункт: {str(e)}")
    
    def _calculate_preview(self):
        """Предварительный расчёт тарифов"""
        try:
            rows = self.sequence_table.rowCount()
            if rows == 0:
                QMessageBox.warning(self, "Внимание", "Нет пунктов для расчёта")
                return
            
            first_row = 0
            global_rounding = float(self.sequence_table.item(first_row, 3).text())
            global_cost_per_km = float(self.sequence_table.item(first_row, 4).text())
            global_baggage_percent = float(self.sequence_table.item(first_row, 5).text())
            
            for row in range(rows):
                distance = float(self.sequence_table.item(row, 2).text())
                tariffs = self.db.calculate_tariffs(
                    distance, global_cost_per_km, global_baggage_percent,
                    global_rounding, self.rounding_checkbox.isChecked()
                )
                
                passenger_item = self._create_item(f"{tariffs['passenger']:.2f}", 
                                                   align=Qt.AlignRight | Qt.AlignVCenter,
                                                   bold=True, editable=False)
                self.sequence_table.setItem(row, 6, passenger_item)
                
                baggage_item = self._create_item(f"{tariffs['baggage']:.2f}", 
                                                 align=Qt.AlignRight | Qt.AlignVCenter,
                                                 editable=False)
                self.sequence_table.setItem(row, 7, baggage_item)
            
            round_type = "в большую сторону" if self.rounding_checkbox.isChecked() else "до ближайшего целого"
            QMessageBox.information(self, "Расчёт выполнен", 
                f"Тарифы пересчитаны с текущими параметрами.\n"
                f"Тип округления: {round_type}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить расчёт: {str(e)}")
    
    def _save_changes(self):
        """Сохранение изменений"""
        try:
            for row in range(self.sequence_table.rowCount()):
                if row >= len(self.original_data):
                    continue
                
                orig = self.original_data[row]
                seq_id = orig['id']
                
                try:
                    new_distance = float(self.sequence_table.item(row, 2).text())
                    if row == 0:
                        new_rounding = float(self.sequence_table.item(row, 3).text())
                        new_cost = float(self.sequence_table.item(row, 4).text())
                        new_baggage = float(self.sequence_table.item(row, 5).text())
                    else:
                        new_rounding = float(orig['rounding'])
                        new_cost = float(orig['cost_per_km'])
                        new_baggage = float(orig['baggage_percent'])
                except (ValueError, AttributeError) as e:
                    QMessageBox.warning(self, "Ошибка", f"Некорректные данные в строке {row + 1}")
                    return
                
                orig_distance = float(orig['distance_km'])
                orig_rounding = float(orig['rounding'])
                orig_cost = float(orig['cost_per_km'])
                orig_baggage = float(orig['baggage_percent'])
                
                if (abs(new_distance - orig_distance) > 0.01 or
                    (row == 0 and (
                        abs(new_rounding - orig_rounding) > 0.01 or
                        abs(new_cost - orig_cost) > 0.01 or
                        abs(new_baggage - orig_baggage) > 0.01
                    ))):
                    
                    self.db.update_route_point(
                        seq_id, new_distance, new_rounding, new_cost, new_baggage
                    )
            
            QMessageBox.information(self, "Успешно", "Изменения сохранены")
            self.load_route_sequence()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _show_cost_table(self):
        """Показать таблицу стоимости"""
        try:
            points = self.db.get_route_sequence(self.route_id)
            if not points:
                QMessageBox.warning(self, "Внимание", "Маршрут пуст")
                return
            
            global_cost_per_km = float(points[0]['cost_per_km'])
            global_baggage_percent = float(points[0]['baggage_percent'])
            global_rounding = float(points[0]['rounding'])
            
            table_text = self._generate_cost_table_text(points, global_cost_per_km,
                                                        global_baggage_percent, global_rounding)
            
            self._show_cost_table_dialog(table_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать таблицу: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _generate_cost_table_text(self, points, cost_per_km, baggage_percent, rounding):
        """Сгенерировать текст таблицы стоимости"""
        table_text = "Таблица стоимости\n"
        table_text += "на проезд и провоз ручной клади и багажа\n"
        table_text += f"в автобусе общего типа по маршруту {self.route_number} — {self.route_name} с __________\n"
        table_text += f"Стоимость 1 п-км: {cost_per_km:.2f}\n\n"
        
        table_text += f"{points[0]['point_name']}\n"
        
        for i in range(1, len(points)):
            line1_parts, line2_parts, line3_parts = [], [], []
            
            for j in range(0, i):
                distance = points[i]['distance_km'] - points[j]['distance_km']
                tariffs = self.db.calculate_tariffs(
                    distance, cost_per_km, baggage_percent, rounding,
                    self.rounding_checkbox.isChecked()
                )
                
                line1_parts.append(f"{tariffs['passenger']:>7.2f}")
                line2_parts.append(f"{tariffs['passenger'] * 0.5:>7.2f}")
                line3_parts.append(f"{tariffs['baggage']:>7.2f}")
            
            table_text += " ".join(line1_parts) + "\n"
            table_text += " ".join(line2_parts) + "\n"
            table_text += " ".join(line3_parts) + "\n"
            table_text += ("        " * i) + f"{points[i]['point_name']}\n\n"
        
        table_text += "Руководитель АТП __________\n"
        return table_text
    
    def _show_cost_table_dialog(self, table_text):
        """Показать диалог с таблицей стоимости"""
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument
        
        cost_dialog = QDialog(self)
        cost_dialog.setWindowTitle("Таблица стоимости")
        cost_dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        text_edit.setLineWrapMode(QTextEdit.NoWrap)
        text_edit.setText(table_text)
        layout.addWidget(text_edit)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Сохранить в TXT")
        save_btn.clicked.connect(lambda: self._save_cost_table_txt(table_text))
        btn_layout.addWidget(save_btn)
        
        print_btn = QPushButton("🖨️ Печать")
        print_btn.clicked.connect(lambda: self._print_cost_table(table_text))
        btn_layout.addWidget(print_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(cost_dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        cost_dialog.setLayout(layout)
        cost_dialog.exec_()
    
    def _save_cost_table_txt(self, table_text):
        """Сохранить таблицу стоимости в TXT"""
        from PyQt5.QtWidgets import QFileDialog
        from datetime import datetime
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Таблица_стоимости_маршрут_{self.route_number}_{current_date}.txt"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить таблицу стоимости", default_filename,
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        
        if filename:
            if not filename.endswith('.txt'):
                filename += '.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(table_text)
            QMessageBox.information(self, "Успешно", f"Таблица сохранена в:\n{filename}")
    
    def _print_cost_table(self, table_text):
        """Напечатать таблицу стоимости"""
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument, QTextOption
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        printer.setPageMargins(5, 5, 5, 5, QPrinter.Millimeter)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            html_text = f"""
            <html><head><style>
                body {{ font-family: 'Courier New', monospace; font-size: 10pt; white-space: pre; }}
                pre {{ font-family: 'Courier New', monospace; font-size: 10pt; margin: 0; padding: 0; }}
            </style></head><body><pre>{table_text}</pre></body></html>
            """
            doc.setHtml(html_text)
            option = QTextOption()
            option.setWrapMode(QTextOption.NoWrap)
            doc.setDefaultTextOption(option)
            doc.print_(printer)
            QMessageBox.information(self, "Успешно", "Таблица отправлена на печать")

    def update_theme(self):
        """Обновить тему диалога"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme_manager.current_theme['window_bg']};
                color: {theme_manager.current_theme['text']};
            }}
            QLabel {{
                color: {theme_manager.current_theme['text']};
            }}
            QCheckBox {{
                color: {theme_manager.current_theme['text']};
            }}
        """)
        
        # Обновляем стили виджетов
        self.points_combo.setStyleSheet(theme_manager.get_input_style())
        self.distance_input.setStyleSheet(theme_manager.get_input_style())
        self.sequence_table.setStyleSheet(theme_manager.get_table_style())
        
        # Обновляем стили кнопок, которые являются атрибутами класса
        self.add_to_route_btn.setStyleSheet(theme_manager.get_button_style("secondary"))
        self.new_point_btn.setStyleSheet(theme_manager.get_button_style("primary"))
        self.calc_btn.setStyleSheet(theme_manager.get_button_style("default"))
        self.save_btn.setStyleSheet(theme_manager.get_button_style("default"))
        
        # Для кнопок, которые не сохранены как атрибуты, нужно найти их в layout
        # или просто не обновлять их здесь (они обновятся при пересоздании диалога)


class EnhancedRouteGridDialog(RouteGridDialog):
    """Расширенная версия диалога с дополнительными функциями"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changes_history = []
        self.modified_rows = set()
        self.current_history_position = -1
        self.max_history_size = 50
        
        self.sequence_table.itemChanged.connect(self._on_table_item_changed)
        self.setup_shortcuts()
    
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # 30 секунд
        
        self.modified = False
    
    def _auto_save(self):
        """Автосохранение изменений"""
        if self.modified:
            reply = QMessageBox.question(
                self, "Автосохранение",
                "Есть несохраненные изменения. Сохранить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._save_changes()
            self.modified = False
    
    def _on_table_item_changed(self, item):
        super()._on_table_item_changed(item)
        self.modified = True

    def setup_shortcuts(self):
        """Добавить клавиатурные сокращения"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        QShortcut(QKeySequence.Save, self, self._save_changes)
        QShortcut(QKeySequence.Delete, self, self._delete_point)
        QShortcut(QKeySequence.Refresh, self, self._calculate_preview)
        QShortcut(QKeySequence.Undo, self, self._undo_change)
        QShortcut(QKeySequence.Redo, self, self._redo_change)
        QShortcut(QKeySequence.Find, self, self._show_search_dialog)
    
    def update_theme(self):
        """Обновить тему для расширенной версии"""
        super().update_theme()
    
    def _on_table_item_changed(self, item):
        """Отслеживание изменений в таблице"""
        row, col = item.row(), item.column()
        if col >= 1:
            self.modified_rows.add(row)
            self._highlight_modified_row(row)
            self._add_to_history({
                'row': row, 'col': col,
                'old_value': self._get_original_value(row, col),
                'new_value': item.text()
            })
    
    def _get_original_value(self, row, col):
        """Получить оригинальное значение"""
        if row < len(self.original_data):
            orig = self.original_data[row]
            if col == 1:
                return orig['point_name']
            elif col == 2:
                return str(orig['distance_km'])
            elif col == 3:
                return str(orig['rounding'])
            elif col == 4:
                return str(orig['cost_per_km'])
            elif col == 5:
                return str(orig['baggage_percent'])
        return ""
    
    def _highlight_modified_row(self, row):
        """Подсветка изменённой строки"""
        for col in range(self.sequence_table.columnCount()):
            item = self.sequence_table.item(row, col)
            if item:
                item.setBackground(QColor(255, 255, 200))
    
    def _add_to_history(self, change):
        """Добавить изменение в историю"""
        if self.current_history_position < len(self.changes_history) - 1:
            self.changes_history = self.changes_history[:self.current_history_position + 1]
        
        self.changes_history.append(change)
        self.current_history_position = len(self.changes_history) - 1
        
        if len(self.changes_history) > self.max_history_size:
            self.changes_history.pop(0)
            self.current_history_position -= 1
    
    def _undo_change(self):
        """Отмена последнего изменения"""
        if self.current_history_position >= 0:
            change = self.changes_history[self.current_history_position]
            item = self.sequence_table.item(change['row'], change['col'])
            if item:
                item.setText(change['old_value'])
            self.current_history_position -= 1
    
    def _redo_change(self):
        """Повтор отменённого изменения"""
        if self.current_history_position < len(self.changes_history) - 1:
            self.current_history_position += 1
            change = self.changes_history[self.current_history_position]
            item = self.sequence_table.item(change['row'], change['col'])
            if item:
                item.setText(change['new_value'])
    
    def _show_search_dialog(self):
        """Показать диалог поиска"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Поиск пункта")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Введите название пункта...")
        layout.addWidget(search_input)
        
        results_list = QListWidget()
        layout.addWidget(results_list)
        
        dialog.setLayout(layout)
        
        def on_search(text):
            results_list.clear()
            search_text = text.lower()
            for row in range(self.sequence_table.rowCount()):
                point_name = self.sequence_table.item(row, 1).text()
                if search_text in point_name.lower():
                    distance = self.sequence_table.item(row, 2).text()
                    results_list.addItem(f"{point_name} (расстояние: {distance} км)")
        
        def on_select(item):
            point_name = item.text().split(" (расстояние:")[0]
            for row in range(self.sequence_table.rowCount()):
                if self.sequence_table.item(row, 1).text() == point_name:
                    self.sequence_table.selectRow(row)
                    self.sequence_table.scrollToItem(
                        self.sequence_table.item(row, 0),
                        QAbstractItemView.PositionAtCenter
                    )
                    dialog.accept()
                    break
        
        search_input.textChanged.connect(on_search)
        results_list.itemClicked.connect(on_select)
        results_list.itemDoubleClicked.connect(on_select)
        
        dialog.exec_()