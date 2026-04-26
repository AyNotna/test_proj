from app.database import SessionLocal, engine
from app.models import Base, SearchQuery
from faker import Faker
import random
from datetime import timedelta


def seed():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        count = db.query(SearchQuery).count()
        if count > 0:
            print(f"База уже заполнена ({count} записей)")
            return
        
        print("Генерирую 11 000 записей...")
        fake = Faker('ru_RU')
        batch = []
        
        for i in range(11000):
            created = fake.date_time_between(start_date='-1y', end_date='now')
            deadline = created + timedelta(days=random.randint(1, 365))
            
            batch.append(SearchQuery(
                name=fake.catch_phrase(),
                created_at=created,
                updated_at=created + timedelta(days=random.randint(0, 30)),
                status=random.choice(["active", "inactive"]),
                owner=fake.email(),
                deadline=deadline,
                results_count=random.randint(0, 10000),
            ))
            
            if len(batch) >= 500:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
                print(f"  {i+1} / 11000")
        
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
        
        print("Создано 11 000 записей")
    
    finally:
        db.close()


if __name__ == "__main__":
    seed()