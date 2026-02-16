"""
Модуль с функциями экспорта и импорта для диалога маршрута
"""
import os
import csv
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt5.QtCore import Qt

from .services import ExportService, ImportService
from .utils import NumberUtils, StringUtils, DateTimeUtils, ValidationUtils

class ExportImportMixin:
    """Миксин с методами экспорта и импорта для RouteGridDialog"""
    
    # ==================== ЭКСПОРТ ====================
    
    def export_route(self):
        """Экспорт маршрута в CSV или Excel"""
        try:
            points = self.db.get_route_sequence(self.route_id)
            if not points:
                QMessageBox.warning(self, "Внимание", "Маршрут пуст")
                return
            
            # Генерируем имя файла
            base_filename = ExportService.generate_filename(
                f"Маршрут_{self.route_number}", 
                extension=""
            )
            
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Сохранить маршрут", base_filename,
                "CSV файлы (*.csv);;Excel файлы (*.xlsx);;PDF файлы (*.pdf);;Все файлы (*.*)"
            )
            
            if not filename:
                return
            
            # Определяем формат
            file_ext = os.path.splitext(filename)[1].lower()
            
            if not file_ext:
                if "CSV" in selected_filter:
                    filename += ".csv"
                    file_ext = ".csv"
                elif "Excel" in selected_filter:
                    filename += ".xlsx"
                    file_ext = ".xlsx"
                elif "PDF" in selected_filter:
                    filename += ".pdf"
                    file_ext = ".pdf"
                else:
                    filename += ".csv"
                    file_ext = ".csv"
            
            # Подготавливаем данные
            headers = ['№ п/п', 'Пункт назначения', 'Расстояние (км)', 
                      'Округление', 'Стоимость за км (₽)', 'Багаж (%)',
                      'Тариф пассажирский (₽)', 'Тариф багаж (₽)']
            
            data = []
            for row in range(self.sequence_table.rowCount()):
                row_data = {}
                for col, header in enumerate(headers):
                    item = self.sequence_table.item(row, col)
                    row_data[header] = item.text() if item else ""
                data.append(row_data)
            
            # Экспортируем в зависимости от формата
            if file_ext == '.csv':
                self._export_to_csv(filename, data, headers)
            elif file_ext == '.xlsx':
                self._export_to_excel(filename, data, headers)
            elif file_ext == '.pdf':
                self._export_to_pdf(filename, data, headers)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _export_to_csv(self, filename, data, headers):
        """Экспорт в CSV"""
        try:
            ExportService.export_to_csv(filename, data, headers)
            QMessageBox.information(self, "Успешно", f"Маршрут экспортирован в CSV")
        except Exception as e:
            raise Exception(f"Ошибка экспорта в CSV: {e}")
    
    def _export_to_excel(self, filename, data, headers):
        """Экспорт в Excel"""
        try:
            ExportService.export_to_excel(
                filename, data, headers, 
                f"Маршрут №{self.route_number}"
            )
            QMessageBox.information(self, "Успешно", f"Маршрут экспортирован в Excel")
        except Exception as e:
            raise Exception(f"Ошибка экспорта в Excel: {e}")
    
    def _export_to_pdf(self, filename, data, headers):
        """Экспорт маршрута в PDF"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            
            # Создаем PDF документ
            doc = SimpleDocTemplate(
                filename, 
                pagesize=landscape(A4),
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1*cm,
                bottomMargin=1*cm
            )
            elements = []
            
            # Стили
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            title_style.alignment = 1  # Центрирование
            
            # Заголовок
            elements.append(Paragraph(
                f"Маршрут №{self.route_number} — {self.route_name}",
                title_style
            ))
            elements.append(Spacer(1, 0.5*cm))
            
            # Дата
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                alignment=2,  # Вправо
                fontSize=10
            )
            elements.append(Paragraph(
                f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                date_style
            ))
            elements.append(Spacer(1, 0.5*cm))
            
            # Подготовка данных для таблицы
            table_data = [headers]  # Заголовки
            
            for row_data in data:
                table_row = []
                for header in headers:
                    table_row.append(row_data.get(header, ''))
                table_data.append(table_row)
            
            # Настройка ширины колонок
            col_widths = [1.5*cm, 5*cm, 2.5*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm]
            
            # Создание таблицы PDF
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                # Заголовок
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                
                # Данные
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Сетка
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                
                # Выравнивание для числовых колонок
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Расстояние
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Округление
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Стоимость
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Багаж %
                ('ALIGN', (6, 1), (6, -1), 'RIGHT'),  # Тариф пасс
                ('ALIGN', (7, 1), (7, -1), 'RIGHT'),  # Тариф багаж
            ]))
            
            # Чередование фона строк
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                    ]))
            
            elements.append(table)
            
            # Подпись внизу
            elements.append(Spacer(1, 1*cm))
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                alignment=2,  # Вправо
                fontSize=10
            )
            elements.append(Paragraph(
                "Руководитель АТП __________________",
                footer_style
            ))
            
            # Сборка PDF
            doc.build(elements)
            
            QMessageBox.information(self, "Успешно", f"PDF сохранен в:\n{filename}")
            
        except ImportError:
            QMessageBox.critical(
                self, "Ошибка", 
                "Библиотека reportlab не установлена.\n"
                "Установите: pip install reportlab"
            )
        except Exception as e:
            raise Exception(f"Ошибка создания PDF: {e}")
    
    # ==================== ИМПОРТ ====================
    
    def import_from_file(self):
        """Импорт пунктов из Excel или CSV файла"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Выберите файл для импорта", "",
                "Поддерживаемые файлы (*.xlsx *.xls *.csv);;"
                "Excel файлы (*.xlsx *.xls);;CSV файлы (*.csv);;Все файлы (*.*)"
            )
            
            if not filename:
                return
            
            progress = QProgressDialog("Импорт данных...", "Отмена", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            # Получаем глобальные параметры
            global_params = self._get_global_parameters()
            
            # Получаем все существующие пункты
            all_points = {p['name'].lower(): p['id'] for p in self.db.get_all_points()}
            
            progress.setValue(30)
            
            # Импортируем данные
            imported_count = 0
            errors = []
            
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                data = ImportService.import_from_excel(filename)
                start_row = 0
            else:
                delimiter = ImportService.detect_delimiter(filename)
                data = ImportService.import_from_csv(filename, delimiter)
                start_row = 0 if data and '№ п/п' in data[0] else 0
            
            progress.setValue(40)
            
            for idx, row_data in enumerate(data):
                if progress.wasCanceled():
                    break
                
                point_name = row_data.get('Пункт назначения', '')
                distance_value = row_data.get('Расстояние (км)', '')
                
                if not point_name or not distance_value:
                    continue
                
                result = self._process_import_row(
                    point_name, distance_value, idx + 2, all_points, global_params
                )
                
                if result['success']:
                    imported_count += 1
                elif result['error']:
                    errors.append(result['error'])
                
                progress.setValue(40 + int(50 * idx / len(data)))
            
            progress.setValue(100)
            
            # Обновляем отображение
            self.load_points()
            self.load_route_sequence()
            
            # Показываем результат
            self._show_import_result(imported_count, errors)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при импорте: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _process_import_row(self, point_name, distance_value, row_num, all_points, global_params):
        """Обработка одной строки импорта"""
        result = {'success': False, 'error': None}
        
        try:
            point_name = StringUtils.normalize(point_name)
            if not point_name:
                return result
            
            # Пропускаем заголовки
            if point_name.lower() in ['пункт назначения', 'название пункта', 'point name']:
                return result
            
            # Преобразуем расстояние
            distance = NumberUtils.parse_number(distance_value)
            if distance <= 0:
                return result
            
            valid, msg = ValidationUtils.validate_distance(distance)
            if not valid:
                result['error'] = f"Строка {row_num}: '{point_name}' - {msg}"
                return result
            
            # Получаем или создаем пункт
            point_id = self._get_or_create_point(point_name, all_points)
            if not point_id:
                result['error'] = f"Строка {row_num}: не удалось создать пункт '{point_name}'"
                return result
            
            # Добавляем в маршрут
            self.db.add_point_to_route(
                self.route_id, point_id, distance,
                global_params['rounding'], 
                global_params['cost_per_km'], 
                global_params['baggage_percent']
            )
            result['success'] = True
            
        except Exception as e:
            result['error'] = f"Строка {row_num}: {str(e)}"
        
        return result