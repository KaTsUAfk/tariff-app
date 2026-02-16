"""Менеджер плагинов"""
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any

class PluginManager:
    def __init__(self):
        self.plugins_dir = Path.home() / '.tariff_app' / 'plugins'
        self.plugins_dir.mkdir(exist_ok=True)
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Загрузить все плагины из папки plugins"""
        sys.path.insert(0, str(self.plugins_dir))
        
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith('_'):
                continue
            
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(
                module_name, plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'register'):
                plugin_info = module.register()
                self.plugins[plugin_info['name']] = {
                    'module': module,
                    'info': plugin_info
                }
    
    def get_exporters(self):
        """Получить все плагины экспорта"""
        return [
            p for p in self.plugins.values() 
            if p['info'].get('type') == 'exporter'
        ]
    
    def get_importers(self):
        """Получить все плагины импорта"""
        return [
            p for p in self.plugins.values() 
            if p['info'].get('type') == 'importer'
        ]