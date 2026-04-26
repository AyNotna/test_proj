from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from app.models import SearchQuery
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Перед каждым тестом пересоздаём таблицы и добавляем тестовые данные"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal
    db = SessionLocal()
    
    now = datetime.utcnow()
    test_data = [
        SearchQuery(
            id=1,
            name="Тестовый запрос 1",
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=5),
            status="active",
            owner="user1@test.com",
            deadline=now + timedelta(days=10),
            results_count=1500,
        ),
        SearchQuery(
            id=2,
            name="Просроченный запрос",
            created_at=now - timedelta(days=60),
            updated_at=now - timedelta(days=20),
            status="active",
            owner="user2@test.com",
            deadline=now - timedelta(days=5),
            results_count=230,
        ),
        SearchQuery(
            id=3,
            name="Неактивный запрос",
            created_at=now - timedelta(days=90),
            updated_at=now - timedelta(days=45),
            status="inactive",
            owner="user3@test.com",
            deadline=now + timedelta(days=30),
            results_count=5000,
        ),
        SearchQuery(
            id=4,
            name="Запрос с большим кол-вом",
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=1),
            status="active",
            owner="user4@test.com",
            deadline=now + timedelta(days=60),
            results_count=9999,
        ),
        SearchQuery(
            id=5,
            name="Запрос пользователя Abc",
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(hours=12),
            status="active",
            owner="abc@test.com",
            deadline=now + timedelta(days=15),
            results_count=42,
        ),
    ]
    
    for item in test_data:
        db.add(item)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)



class TestGetQueries:
    """Тесты получения списка запросов"""

    def test_get_all_queries(self):
        """Получение всех записей (без параметров)"""
        response = client.get("/api/queries/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert data["total"] == 5
        assert len(data["data"]) == 5

    def test_pagination_limit(self):
        """Пагинация: limit=2"""
        response = client.get("/api/queries/?page=1&limit=2")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1

    def test_pagination_second_page(self):
        """Пагинация: вторая страница"""
        response = client.get("/api/queries/?page=2&limit=2")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 2

    def test_pagination_out_of_range(self):
        """Пагинация: страница за пределами (должен быть пустой массив)"""
        response = client.get("/api/queries/?page=100&limit=20")
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 5

    def test_sort_by_name_asc(self):
        """Сортировка по названию (по возрастанию)"""
        response = client.get("/api/queries/?sort=name&order=asc")
        data = response.json()
        names = [item["name"] for item in data["data"]]
        assert names == sorted(names)

    def test_sort_by_name_desc(self):
        """Сортировка по названию (по убыванию)"""
        response = client.get("/api/queries/?sort=name&order=desc")
        data = response.json()
        names = [item["name"] for item in data["data"]]
        assert names == sorted(names, reverse=True)

    def test_sort_by_results_count(self):
        """Сортировка по количеству результатов"""
        response = client.get("/api/queries/?sort=results_count&order=asc")
        data = response.json()
        counts = [item["results_count"] for item in data["data"]]
        assert counts == sorted(counts)

    def test_sort_by_results_count_desc(self):
        """Сортировка по количеству результатов (убывание)"""
        response = client.get("/api/queries/?sort=results_count&order=desc")
        data = response.json()
        counts = [item["results_count"] for item in data["data"]]
        assert counts == sorted(counts, reverse=True)

    def test_sort_by_created_at(self):
        """Сортировка по дате создания"""
        response = client.get("/api/queries/?sort=created_at&order=asc")
        data = response.json()
        dates = [item["created_at"] for item in data["data"]]
        assert dates == sorted(dates)

    def test_sort_invalid_field(self):
        """Некорректное поле сортировки — должно быть по умолчанию (created_at)"""
        response = client.get("/api/queries/?sort=invalid_field&order=asc")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5

    def test_overdue_flag(self):
        """Проверка флага is_overdue для просроченного запроса"""
        response = client.get("/api/queries/")
        data = response.json()
        overdue_items = [item for item in data["data"] if item["is_overdue"]]
        assert len(overdue_items) == 1
        assert overdue_items[0]["name"] == "Просроченный запрос"

    def test_overdue_not_for_inactive(self):
        """Неактивный запрос не должен быть просроченным, даже если дедлайн прошёл"""
        response = client.get("/api/queries/")
        data = response.json()
        inactive_item = [item for item in data["data"] if item["status"] == "inactive"][0]
        assert inactive_item["is_overdue"] == False



class TestCreateQuery:
    """Тесты создания запроса"""

    def test_create_query_success(self):
        """Успешное создание нового запроса"""
        new_query = {
            "name": "Новый поисковый запрос",
            "status": "active",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        response = client.post("/api/queries/", json=new_query)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новый поисковый запрос"
        assert data["status"] == "active"
        assert "id" in data
        assert "owner" in data
        assert "results_count" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_query_inactive(self):
        """Создание неактивного запроса"""
        new_query = {
            "name": "Неактивный запрос",
            "status": "inactive",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        response = client.post("/api/queries/", json=new_query)
        assert response.status_code == 200
        assert response.json()["status"] == "inactive"

    def test_create_query_missing_name(self):
        """Создание без названия — ошибка валидации"""
        new_query = {
            "status": "active",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        response = client.post("/api/queries/", json=new_query)
        assert response.status_code == 422  

    def test_create_query_empty_name(self):
        """Создание с пустым названием"""
        new_query = {
            "name": "",
            "status": "active",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        response = client.post("/api/queries/", json=new_query)
        assert response.status_code == 200

    def test_create_query_increases_total(self):
        """После создания общее количество увеличивается"""
        before = client.get("/api/queries/").json()["total"]
        client.post("/api/queries/", json={
            "name": "Тест увеличения",
            "status": "active",
            "deadline": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        })
        after = client.get("/api/queries/").json()["total"]
        assert after == before + 1


class TestUpdateQuery:
    """Тесты редактирования запроса"""

    def test_update_name(self):
        """Изменение названия"""
        response = client.put("/api/queries/1", json={"name": "Обновлённое название"})
        assert response.status_code == 200
        assert response.json()["name"] == "Обновлённое название"

    def test_update_status(self):
        """Изменение статуса"""
        response = client.put("/api/queries/1", json={"status": "inactive"})
        assert response.status_code == 200
        assert response.json()["status"] == "inactive"

    def test_update_deadline(self):
        """Изменение дедлайна"""
        new_deadline = (datetime.utcnow() + timedelta(days=100)).isoformat()
        response = client.put("/api/queries/1", json={"deadline": new_deadline})
        assert response.status_code == 200

    def test_update_multiple_fields(self):
        """Изменение нескольких полей одновременно"""
        response = client.put("/api/queries/1", json={
            "name": "Полностью новый",
            "status": "inactive",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Полностью новый"
        assert data["status"] == "inactive"

    def test_update_nonexistent(self):
        """Обновление несуществующей записи"""
        response = client.put("/api/queries/99999", json={"name": "Неважно"})
        assert response.status_code == 404

    def test_update_no_fields(self):
        """Запрос без полей для обновления"""
        response = client.put("/api/queries/1", json={})
        assert response.status_code == 200



class TestDeleteQuery:
    """Тесты удаления одной записи"""

    def test_delete_existing(self):
        """Удаление существующей записи"""
        response = client.delete("/api/queries/1")
        assert response.status_code == 200
        assert response.json()["ok"] == True

    def test_delete_removes_record(self):
        """После удаления запись недоступна"""
        client.delete("/api/queries/1")
        response = client.put("/api/queries/1", json={"name": "Test"})
        assert response.status_code == 404

    def test_delete_decreases_total(self):
        """После удаления общее количество уменьшается"""
        before = client.get("/api/queries/").json()["total"]
        client.delete("/api/queries/1")
        after = client.get("/api/queries/").json()["total"]
        assert after == before - 1

    def test_delete_nonexistent(self):
        """Удаление несуществующей записи"""
        response = client.delete("/api/queries/99999")
        assert response.status_code == 404


class TestDeleteMany:
    """Тесты группового удаления"""

    def test_delete_multiple(self):
        """Удаление нескольких записей"""
        response = client.post("/api/queries/delete-many", json=[1, 2, 3])
        assert response.status_code == 200
        assert response.json()["ok"] == True
        assert response.json()["deleted"] == 3

    def test_delete_multiple_reduces_total(self):
        """Проверка уменьшения общего количества"""
        before = client.get("/api/queries/").json()["total"]
        client.post("/api/queries/delete-many", json=[1, 2])
        after = client.get("/api/queries/").json()["total"]
        assert after == before - 2

    def test_delete_empty_list(self):
        """Удаление пустого списка — ничего не происходит"""
        response = client.post("/api/queries/delete-many", json=[])
        assert response.status_code == 200
        assert response.json()["deleted"] == 0

    def test_delete_nonexistent_ids(self):
        """Удаление несуществующих id — без ошибки"""
        response = client.post("/api/queries/delete-many", json=[99998, 99999])
        assert response.status_code == 200
        assert response.json()["deleted"] == 0

    def test_delete_mixed_ids(self):
        """Удаление смешанных id (существующие + нет)"""
        response = client.post("/api/queries/delete-many", json=[1, 99999])
        assert response.status_code == 200
        assert response.json()["deleted"] == 1




class TestEdgeCases:
    """Тесты на крайние случаи"""

    def test_large_limit(self):
        """Запрос с максимальным лимитом (100)"""
        response = client.get("/api/queries/?limit=100")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 5

    def test_page_zero(self):
        """Некорректная страница (0) — должен вернуть ошибку валидации"""
        response = client.get("/api/queries/?page=0")
        assert response.status_code == 422

    def test_negative_limit(self):
        """Отрицательный лимит — ошибка валидации"""
        response = client.get("/api/queries/?limit=-1")
        assert response.status_code == 422

    def test_too_large_limit(self):
        """Слишком большой лимит — ошибка валидации"""
        response = client.get("/api/queries/?limit=101")
        assert response.status_code == 422

    def test_response_structure(self):
        """Проверка структуры ответа (все поля на месте)"""
        response = client.get("/api/queries/")
        data = response.json()["data"][0]
        required_fields = [
            "id", "name", "created_at", "updated_at",
            "status", "owner", "deadline", "results_count", "is_overdue"
        ]
        for field in required_fields:
            assert field in data, f"Поле {field} отсутствует в ответе"