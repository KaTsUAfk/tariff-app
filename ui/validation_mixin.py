"""
Модуль с функциями валидации для диалога маршрута
"""
from PyQt5.QtWidgets import QMessageBox
from .utils import ValidationUtils, NumberUtils

class ValidationMixin:
    """Миксин с методами валидации для RouteGridDialog"""
    
    def _validate_tariff_data(self):
        """Проверка корректности введённых данных"""
        rows = self.sequence_table.rowCount()
        if rows == 0:
            return False, "Маршрут пуст"
        
        for row in range(rows):
            try:
                # Проверка расстояния
                distance_text = self.sequence_table.item(row, 2).text()
                distance = NumberUtils.parse_number(distance_text)
                
                valid, msg = ValidationUtils.validate_distance(distance)
                if not valid:
                    return False, f"Строка {row + 1}: {msg}"
                
                if row == 0 and abs(distance) > 0.01:
                    return False, "Первый пункт должен иметь расстояние 0 км"
                
                # Проверка округления (только для первого пункта)
                if row == 0:
                    rounding_text = self.sequence_table.item(row, 3).text()
                    rounding = NumberUtils.parse_number(rounding_text)
                    if rounding < 0:
                        return False, f"Отрицательное значение округления в строке {row + 1}"
                
                # Проверка стоимости за км (только для первого пункта)
                if row == 0:
                    cost_text = self.sequence_table.item(row, 4).text()
                    cost = NumberUtils.parse_number(cost_text)
                    valid, msg = ValidationUtils.validate_cost(cost)
                    if not valid:
                        return False, f"Строка {row + 1}: {msg}"
                
                # Проверка процента багажа (только для первого пункта)
                if row == 0:
                    baggage_text = self.sequence_table.item(row, 5).text()
                    baggage = NumberUtils.parse_number(baggage_text)
                    valid, msg = ValidationUtils.validate_percentage(baggage)
                    if not valid:
                        return False, f"Строка {row + 1}: {msg}"
                        
            except AttributeError:
                return False, f"Пустая ячейка в строке {row + 1}"
        
        return True, "OK"
    
    def _validate_and_show(self):
        """Проверка данных и показ результата"""
        is_valid, message = self._validate_tariff_data()
        
        if is_valid:
            QMessageBox.information(self, "Проверка данных", 
                "✅ Все данные корректны", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Ошибка в данных", 
                f"❌ {message}", QMessageBox.Ok)
        return is_valid, message

    def _get_tariff_data(self):
        """Получить данные тарифа из таблицы"""
        rows = self.sequence_table.rowCount()
        tariff_data = []
        for row in range(rows):
            distance = NumberUtils.parse_number(self.sequence_table.item(row, 2).text())
            rounding = NumberUtils.parse_number(self.sequence_table.item(row, 3).text())
            cost = NumberUtils.parse_number(self.sequence_table.item(row, 4).text())
            baggage = NumberUtils.parse_number(self.sequence_table.item(row, 5).text())
            tariff_data.append({
                'distance': distance,
                'rounding': rounding,
                'cost': cost,
                'baggage': baggage
            })
        return tariff_data

