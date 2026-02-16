"""
Декораторы для обработки ошибок и повторяющихся операций
"""
from functools import wraps
from PyQt5.QtWidgets import QMessageBox
import traceback

def handle_exceptions(parent=None, error_message="Произошла ошибка"):
    """Декоратор для обработки исключений"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                parent_widget = parent if parent else self
                if hasattr(parent_widget, 'show_error'):
                    parent_widget.show_error(error_message, str(e))
                else:
                    QMessageBox.critical(parent_widget, error_message, str(e))
                traceback.print_exc()
        return wrapper
    return decorator

def confirm_action(title="Подтверждение", message="Вы уверены?"):
    """Декоратор для подтверждения действия"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'show_question'):
                if self.show_question(title, message):
                    return func(self, *args, **kwargs)
            else:
                reply = QMessageBox.question(
                    self, title, message,
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    return func(self, *args, **kwargs)
        return wrapper
    return decorator

def validate_input(validation_func, error_message="Некорректный ввод"):
    """Декоратор для валидации входных данных"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if validation_func(self, *args, **kwargs):
                return func(self, *args, **kwargs)
            else:
                if hasattr(self, 'show_warning'):
                    self.show_warning("Ошибка валидации", error_message)
                else:
                    QMessageBox.warning(self, "Ошибка валидации", error_message)
        return wrapper
    return decorator

def show_progress(message="Загрузка..."):
    """Декоратор для отображения прогресса"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            from PyQt5.QtWidgets import QProgressDialog
            from PyQt5.QtCore import Qt
            
            progress = QProgressDialog(message, "Отмена", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(0)
            
            try:
                result = func(self, *args, **kwargs)
                progress.setValue(100)
                return result
            except Exception as e:
                progress.close()
                raise e
            finally:
                progress.close()
        return wrapper
    return decorator

def retry_on_failure(max_retries=3, delay=1000):
    """Декоратор для повторных попыток при ошибке"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            from PyQt5.QtCore import QTimer
            from PyQt5.QtWidgets import QApplication
            
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        QApplication.processEvents()
                        QTimer.singleShot(delay, None)
                        QApplication.processEvents()
            
            raise last_error
        return wrapper
    return decorator