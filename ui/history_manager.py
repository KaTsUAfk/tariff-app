"""
Менеджер истории действий (Undo/Redo)
"""
from typing import List, Dict, Any, Optional
from collections import deque
from dataclasses import dataclass, field


@dataclass
class HistoryEntry:
    """Запись в истории"""
    action: str  # 'add', 'edit', 'delete', 'sort'
    data: Dict[str, Any]
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    description: str = ""


class HistoryManager:
    """Менеджер для управления историей действий"""
    
    def __init__(self, max_size: int = 50):
        self.undo_stack: deque = deque(maxlen=max_size)
        self.redo_stack: deque = deque(maxlen=max_size)
        self.max_size = max_size
    
    def add_action(self, action: str, data: Dict[str, Any], description: str = "") -> None:
        """Добавить действие в историю"""
        entry = HistoryEntry(action=action, data=data, description=description)
        self.undo_stack.append(entry)
        self.redo_stack.clear()  # Очищаем redo при новом действии
    
    def can_undo(self) -> bool:
        """Можно ли отменить действие"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Можно ли повторить действие"""
        return len(self.redo_stack) > 0
    
    def undo(self) -> Optional[HistoryEntry]:
        """Отменить последнее действие"""
        if not self.can_undo():
            return None
        entry = self.undo_stack.pop()
        self.redo_stack.append(entry)
        return entry
    
    def redo(self) -> Optional[HistoryEntry]:
        """Повторить отменённое действие"""
        if not self.can_redo():
            return None
        entry = self.redo_stack.pop()
        self.undo_stack.append(entry)
        return entry
    
    def clear(self) -> None:
        """Очистить историю"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_description(self) -> str:
        """Получить описание последнего действия для отмены"""
        if not self.can_undo():
            return ""
        return self.undo_stack[-1].description
    
    def get_redo_description(self) -> str:
        """Получить описание следующего действия для повтора"""
        if not self.can_redo():
            return ""
        return self.redo_stack[-1].description
    
    def get_undo_description(self):
        """Получить описание действия для отмены"""
        if not self.can_undo():
            return ""
        return self.undo_stack[-1].description
    
    def get_redo_description(self):
        """Получить описание действия для повтора"""
        if not self.can_redo():
            return ""
        return self.redo_stack[-1].description


class HistoryMixin:
    """Миксин для добавления истории в классы"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = HistoryManager()
    
    def _add_to_history(self, action: str, data: Dict[str, Any], description: str = "") -> None:
        """Добавить действие в историю"""
        self.history.add_action(action, data, description)
    
    def _undo(self) -> bool:
        """Отменить последнее действие"""
        entry = self.history.undo()
        if entry:
            self._apply_history_entry(entry, undo=True)
            return True
        return False
    
    def _redo(self) -> bool:
        """Повторить отменённое действие"""
        entry = self.history.redo()
        if entry:
            self._apply_history_entry(entry, undo=False)
            return True
        return False
    
    def _apply_history_entry(self, entry: HistoryEntry, undo: bool) -> None:
        """Применить запись истории (должен быть переопределён)"""
        raise NotImplementedError("Метод _apply_history_entry должен быть реализован в классе-наследнике")