"""Проверка обновлений приложения"""
import json
import urllib.request
import urllib.error
from packaging import version
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

class UpdateChecker(QThread):
    """Поток для проверки обновлений"""
    update_available = pyqtSignal(str, str, list)
    check_failed = pyqtSignal(str)
    
    def __init__(self, current_version, github_repo="KaTsUAfk/tariff-app"):
        super().__init__()
        self.current_version = current_version
        self.github_repo = github_repo
        self.check_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
    
    def run(self):
        """Запуск проверки в отдельном потоке"""
        try:
            # Пытаемся получить информацию о последнем релизе с GitHub
            req = urllib.request.Request(
                self.check_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data['tag_name'].lstrip('v')
                
                # Сравниваем версии
                if version.parse(latest_version) > version.parse(self.current_version):
                    # Есть новая версия
                    self.update_available.emit(
                        latest_version,
                        data['html_url'],
                        data.get('body', '').split('\n')
                    )
        
        except urllib.error.URLError as e:
            # Не удалось подключиться к GitHub, пробуем локальный файл
            self._check_local_version()
        except Exception as e:
            self.check_failed.emit(str(e))
    
    def _check_local_version(self):
        """Проверка по локальному файлу version.json"""
        try:
            import os
            from pathlib import Path
            
            version_file = Path(__file__).parent.parent / 'version.json'
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                latest_version = data.get('version', '0.0.0')
                if version.parse(latest_version) > version.parse(self.current_version):
                    self.update_available.emit(
                        latest_version,
                        data.get('download_url', ''),
                        data.get('changes', [])
                    )
        except:
            pass  # Игнорируем ошибки локальной проверки


class UpdateManager:
    """Менеджер обновлений"""
    
    def __init__(self, parent, current_version="1.0.0", github_repo="yourusername/tariff-app"):
        self.parent = parent
        self.current_version = current_version
        self.github_repo = github_repo
        self.checker = None
    
    def check_for_updates(self, silent=True):
        """Проверить наличие обновлений"""
        self.checker = UpdateChecker(self.current_version, self.github_repo)
        self.checker.update_available.connect(self._on_update_available)
        self.checker.check_failed.connect(lambda e: self._on_check_failed(e, silent))
        self.checker.start()
    
    def _on_update_available(self, version, url, changes):
        """Обработчик наличия обновления"""
        changes_text = "\n".join([f"• {change}" for change in changes[:5]])
        if len(changes) > 5:
            changes_text += f"\n• ... и еще {len(changes) - 5} изменений"
        
        reply = QMessageBox.question(
            self.parent,
            "Доступно обновление",
            f"Доступна новая версия {version}\n\n"
            f"Текущая версия: {self.current_version}\n\n"
            f"Что нового:\n{changes_text}\n\n"
            "Хотите перейти на страницу загрузки?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import webbrowser
            webbrowser.open(url)
    
    def _on_check_failed(self, error, silent):
        """Обработчик ошибки проверки"""
        if not silent:
            QMessageBox.warning(
                self.parent,
                "Ошибка проверки",
                f"Не удалось проверить обновления:\n{error}"
            )