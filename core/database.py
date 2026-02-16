"""
database.py
Модуль работы с базой данных для тарифных сеток
"""
import math
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple, Union
import logging
from decimal import Decimal
from contextlib import contextmanager  # Добавьте эту строку
from core.config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Пользовательское исключение для ошибок работы с БД"""
    pass

class Database:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self) -> None:
        """
        Инициализация подключения к базе данных.
        
        Raises:
            DatabaseError: При ошибке подключения к БД
        """
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                dbname=DB_CONFIG["dbname"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                client_encoding='UTF8'
            )
            self.conn.autocommit = False
            logger.info("Подключение к БД установлено")
        except Exception as e:
            raise DatabaseError(f"Не удалось подключиться к БД: {e}")
    
    def _ensure_connection(self) -> None:
        """Проверка и восстановление подключения при необходимости"""
        if not hasattr(self, 'conn') or self.conn.closed:
            self.__init__()
    
    def close(self) -> None:
        """Закрыть соединение с базой данных"""
        if hasattr(self, 'conn') and self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Подключение к БД закрыто")
    
    @contextmanager
    def transaction(self):
        """Контекстный менеджер для транзакций"""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
    
    @contextmanager
    def cursor(self):
        """Контекстный менеджер для курсора"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()
    
    # === Пункты ===
    def get_all_points(self) -> List[Dict[str, Union[int, str]]]:
        """
        Получить список всех пунктов.
        
        Returns:
            List[Dict]: Список пунктов с полями:
                - id: int
                - name: str
        """
        self._ensure_connection()
        try:
            with self.cursor() as cur:
                cur.execute("SELECT id, name FROM points ORDER BY name")
                result = cur.fetchall()
                return list(result) if result is not None else []
        except Exception as e:
            logger.error(f"Ошибка при получении пунктов: {e}")
            return []
    
    def add_point(self, name: str) -> int:
        """
        Добавить новый пункт назначения.
        
        Args:
            name: Название пункта
            
        Returns:
            int: ID созданного пункта
        """
        clean_name = name.strip()
        if not clean_name:
            raise DatabaseError("Название пункта не может быть пустым")
        
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                # Проверка существования
                cur.execute(
                    "SELECT id, name FROM points WHERE LOWER(TRIM(name)) = LOWER(%s)",
                    (clean_name,)
                )
                existing = cur.fetchone()
                if existing:
                    raise DatabaseError(
                        f"Пункт '{clean_name}' уже существует в базе (ID={existing[0]})"
                    )
                
                # Добавление
                cur.execute(
                    "INSERT INTO points (name) VALUES (%s) RETURNING id",
                    (clean_name,)
                )
                point_id = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Добавлен пункт: {clean_name} (ID={point_id})")
                return point_id
                
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка уникальности: {e}")
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка добавления пункта: {e}")
    
    def update_point(self, point_id: int, name: str) -> bool:
        """Обновить пункт"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE points SET name = %s WHERE id = %s", (name.strip(), point_id))
                self.conn.commit()
                return cur.rowcount > 0
        except psycopg2.IntegrityError:
            self.conn.rollback()
            raise DatabaseError(f"Пункт '{name}' уже существует")
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка обновления пункта: {e}")
    
    def delete_point(self, point_id: int) -> bool:
        """Удалить пункт"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM route_sequence WHERE point_id = %s", (point_id,))
                if cur.fetchone()[0] > 0:
                    raise DatabaseError("Нельзя удалить пункт: он используется в маршрутах")
                cur.execute("DELETE FROM points WHERE id = %s", (point_id,))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка удаления пункта: {e}")
    
    def search_points(self, query: str) -> List[Dict]:
        """Поиск пунктов"""
        self._ensure_connection()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM points WHERE name ILIKE %s ORDER BY name", (f"%{query}%",))
            return cur.fetchall()
    
    # === Маршруты ===
    def get_all_routes(self) -> List[Dict]:
        """Получить все маршруты"""
        self._ensure_connection()
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT r.*, COUNT(rs.id) as points_count
                    FROM routes r
                    LEFT JOIN route_sequence rs ON r.id = rs.route_id
                    GROUP BY r.id
                    ORDER BY r.route_number
                """)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении маршрутов: {e}")
            return []
    
    def add_route(self, route_number: str, route_name: str) -> int:
        """Добавить маршрут"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO routes (route_number, route_name) VALUES (%s, %s) RETURNING id",
                           (route_number.strip(), route_name.strip()))
                route_id = cur.fetchone()[0]
                self.conn.commit()
                return route_id
        except psycopg2.IntegrityError:
            self.conn.rollback()
            raise DatabaseError(f"Маршрут с номером '{route_number}' уже существует")
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка добавления маршрута: {e}")
    
    def delete_route(self, route_id: int) -> bool:
        """Удалить маршрут"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM routes WHERE id = %s", (route_id,))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка удаления маршрута: {e}")
    
    def get_route_by_id(self, route_id: int) -> Optional[Dict]:
        """Получить маршрут по ID"""
        self._ensure_connection()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM routes WHERE id = %s", (route_id,))
            return cur.fetchone()
    
    def update_route(self, route_id: int, route_number: str, route_name: str) -> bool:
        """Обновить маршрут"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE routes SET route_number = %s, route_name = %s WHERE id = %s",
                           (route_number.strip(), route_name.strip(), route_id))
                self.conn.commit()
                return cur.rowcount > 0
        except psycopg2.IntegrityError:
            self.conn.rollback()
            raise DatabaseError(f"Маршрут с номером '{route_number}' уже существует")
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка обновления маршрута: {e}")
    
    # === Последовательность пунктов ===
    def get_route_sequence(self, route_id: int) -> List[Dict]:
        """Получить последовательность пунктов маршрута"""
        self._ensure_connection()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT rs.*, p.name as point_name
                FROM route_sequence rs
                JOIN points p ON rs.point_id = p.id
                WHERE rs.route_id = %s
                ORDER BY rs.sequence_number
            """, (route_id,))
            return cur.fetchall()
    
    def add_point_to_route(self, route_id: int, point_id: int, distance_km: float = 0.0,
                          rounding: float = 0.0, cost_per_km: float = 10.0, 
                          baggage_percent: float = 0.0):
        """Добавить пункт в конец маршрута"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM route_sequence WHERE route_id = %s", (route_id,))
                next_seq = cur.fetchone()[0]
                
                cur.execute("""
                    INSERT INTO route_sequence 
                    (route_id, point_id, sequence_number, distance_km, rounding, cost_per_km, baggage_percent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (route_id, point_id, next_seq, distance_km, rounding, cost_per_km, baggage_percent))
                self.conn.commit()
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            if "unique constraint" in str(e):
                raise DatabaseError("Этот пункт уже добавлен в маршрут")
            raise DatabaseError(f"Ошибка добавления пункта: {e}")
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка добавления пункта: {e}")
    
    def update_route_point(self, seq_id: int, distance_km: float, rounding: float,
                          cost_per_km: float, baggage_percent: float):
        """Обновить параметры пункта маршрута"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE route_sequence 
                    SET distance_km = %s, rounding = %s, cost_per_km = %s, baggage_percent = %s
                    WHERE id = %s
                """, (distance_km, rounding, cost_per_km, baggage_percent, seq_id))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка обновления пункта: {e}")
    
    def remove_point_from_route(self, route_sequence_id: int):
        """Удалить пункт из маршрута"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT route_id, sequence_number FROM route_sequence WHERE id = %s", (route_sequence_id,))
                route_id, seq_num = cur.fetchone()
                
                cur.execute("DELETE FROM route_sequence WHERE id = %s", (route_sequence_id,))
                cur.execute("""
                    UPDATE route_sequence 
                    SET sequence_number = sequence_number - 1 
                    WHERE route_id = %s AND sequence_number > %s
                """, (route_id, seq_num))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка удаления пункта: {e}")
    
    # === Расчёт тарифов ===
    def calculate_tariffs(self, distance: float, cost_per_km: float, 
                        baggage_percent: float, rounding: float = 0.0, 
                        round_up: bool = False) -> Dict[str, float]:
        """Расчёт тарифов с выбором типа округления"""
        try:
            # Безопасное преобразование в float
            distance = float(distance) if distance is not None else 0
            cost_per_km = float(cost_per_km) if cost_per_km is not None else 0
            baggage_percent = float(baggage_percent) if baggage_percent is not None else 0
            rounding = float(rounding) if rounding is not None else 0
        except (TypeError, ValueError):
            return {'passenger': 0.0, 'baggage': 0.0}
        
        # Валидация входных данных
        if distance <= 0 or cost_per_km <= 0:
            return {'passenger': 0.0, 'baggage': 0.0}
        
        # Тариф пассажирский = расстояние × стоимость за км
        passenger = distance * cost_per_km
        
        # Применяем округление ТОЛЬКО если rounding > 0
        if rounding > 0:
            if round_up:
                # Округление в большую сторону
                passenger = math.ceil(passenger / rounding) * rounding
            else:
                # Обычное округление до ближайшего целого
                passenger = round(passenger / rounding) * rounding
        
        # Тариф багаж
        if baggage_percent > 0:
            baggage = (cost_per_km * (baggage_percent / 100)) * distance
            if rounding > 0:
                if round_up:
                    baggage = math.ceil(baggage / rounding) * rounding
                else:
                    baggage = round(baggage / rounding) * rounding
        else:
            baggage = 0.0
        
        return {
            'passenger': round(passenger, 2),
            'baggage': round(baggage, 2)
        }

    def update_route_sequence_number(self, seq_id: int, new_number: int):
        """Обновить порядковый номер пункта в маршруте"""
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                # Сначала получаем текущий номер и route_id
                cur.execute("SELECT sequence_number, route_id FROM route_sequence WHERE id = %s", (seq_id,))
                result = cur.fetchone()
                if not result:
                    return False
                
                old_number, route_id = result
                
                if old_number == new_number:
                    return True
                
                # Получаем максимальный номер для временных значений
                cur.execute("SELECT MAX(sequence_number) FROM route_sequence WHERE route_id = %s", (route_id,))
                max_seq = cur.fetchone()[0] or 0
                temp_base = max_seq + 100
                
                # Сначала перемещаем целевую запись во временное место
                temp_number = temp_base + 1
                cur.execute("""
                    UPDATE route_sequence 
                    SET sequence_number = %s 
                    WHERE id = %s
                """, (temp_number, seq_id))
                
                # Сдвигаем остальные записи
                if new_number > old_number:
                    # Перемещение вниз: сдвигаем записи между old+1 и new вверх
                    cur.execute("""
                        UPDATE route_sequence 
                        SET sequence_number = sequence_number - 1 
                        WHERE route_id = %s 
                        AND sequence_number > %s 
                        AND sequence_number <= %s
                    """, (route_id, old_number, new_number))
                else:
                    # Перемещение вверх: сдвигаем записи между new и old-1 вниз
                    cur.execute("""
                        UPDATE route_sequence 
                        SET sequence_number = sequence_number + 1 
                        WHERE route_id = %s 
                        AND sequence_number >= %s 
                        AND sequence_number < %s
                    """, (route_id, new_number, old_number))
                
                # Возвращаем целевую запись на нужное место
                cur.execute("""
                    UPDATE route_sequence 
                    SET sequence_number = %s 
                    WHERE id = %s
                """, (new_number, seq_id))
                
                self.conn.commit()
                return True
                
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка обновления порядка пункта: {e}")
        
    def reorder_route_sequence(self, route_id: int, new_order: List[int]):
        """
        Переупорядочить пункты маршрута
        new_order - список ID записей в новом порядке
        """
        self._ensure_connection()
        try:
            with self.conn.cursor() as cur:
                # Получаем максимальный sequence_number для этого маршрута
                cur.execute("SELECT MAX(sequence_number) FROM route_sequence WHERE route_id = %s", (route_id,))
                max_seq = cur.fetchone()[0] or 0
                
                # Используем временные номера в допустимом диапазоне (начиная с max_seq + 100)
                temp_base = max_seq + 100
                
                # Сначала присваиваем временные номера в правильном порядке
                for new_position, seq_id in enumerate(new_order):
                    temp_number = temp_base + new_position + 1
                    cur.execute("""
                        UPDATE route_sequence 
                        SET sequence_number = %s 
                        WHERE id = %s AND route_id = %s
                    """, (temp_number, seq_id, route_id))
                
                # Затем устанавливаем правильные номера (1, 2, 3...)
                for new_position, seq_id in enumerate(new_order):
                    cur.execute("""
                        UPDATE route_sequence 
                        SET sequence_number = %s 
                        WHERE id = %s AND route_id = %s
                    """, (new_position + 1, seq_id, route_id))
                
                self.conn.commit()
                return True
                
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Ошибка переупорядочивания маршрута: {e}")