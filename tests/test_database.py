"""
Тесты для модуля database.py
"""
import pytest
from unittest.mock import Mock, patch
from database import Database, DatabaseError

class TestDatabase:
    @pytest.fixture
    def db(self):
        """Фикстура для создания экземпляра Database"""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            db = Database()
            yield db
    
    def test_get_all_points_success(self, db):
        """Тест успешного получения всех пунктов"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Курган'},
            {'id': 2, 'name': 'Варгаши'}
        ]
        
        with patch.object(db.conn, 'cursor', return_value=mock_cursor):
            points = db.get_all_points()
            assert len(points) == 2
            assert points[0]['name'] == 'Курган'
    
    def test_get_all_points_empty(self, db):
        """Тест получения пустого списка пунктов"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        
        with patch.object(db.conn, 'cursor', return_value=mock_cursor):
            points = db.get_all_points()
            assert len(points) == 0
    
    def test_add_point_duplicate(self, db):
        """Тест добавления дубликата пункта"""
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [(1, 'Курган'), None]
        
        with patch.object(db.conn, 'cursor', return_value=mock_cursor):
            with pytest.raises(DatabaseError, match="уже существует"):
                db.add_point("Курган")
    
    def test_calculate_tariffs_normal(self, db):
        """Тест расчета тарифов"""
        result = db.calculate_tariffs(
            distance=100.0,
            cost_per_km=10.0,
            baggage_percent=50.0,
            rounding=1.0,
            round_up=False
        )
        
        assert result['passenger'] == 1000.0  # 100 * 10
        assert result['baggage'] == 500.0  # 100 * 10 * 0.5