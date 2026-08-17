import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import Base

# Use separate test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_brewpredict.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "BrewPredict" in response.text

def test_tea_crud_and_brews_analytics():
    # 1. Create a Tea
    tea_data = {"name": "Test Matcha", "flavor": "Sweet, Umami", "price": 18.50}
    response = client.post("/teas", json=tea_data)
    assert response.status_code == 201
    created_tea = response.json()
    assert created_tea["name"] == "Test Matcha"
    assert created_tea["id"] is not None

    # 2. Get all teas
    response = client.get("/teas")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # 3. Get single tea
    tea_id = created_tea["id"]
    response = client.get(f"/teas/{tea_id}")
    assert response.status_code == 200
    assert response.json()["flavor"] == "Sweet, Umami"

    # 4. Log a Brew Session
    brew_data = {"tea_id": tea_id, "duration_seconds": 120, "rating": 4}
    response = client.post("/brews", json=brew_data)
    assert response.status_code == 201
    created_brew = response.json()
    assert created_brew["tea_id"] == tea_id
    assert created_brew["rating"] == 4

    # 5. Get all brews
    response = client.get("/brews")
    assert response.status_code == 200
    brews_list = response.json()
    assert len(brews_list) == 1
    assert brews_list[0]["tea_name"] == "Test Matcha"

    # 6. Fetch Analytics
    response = client.get("/analytics")
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["total_teas"] == 1
    assert analytics["total_brews"] == 1
    assert analytics["average_price"] == 18.5
    assert analytics["average_rating"] == 4.0

    # 7. Delete Tea
    response = client.delete(f"/teas/{tea_id}")
    assert response.status_code == 200
    
    # 8. Verify deletion cascades or leaves correct state
    response = client.get(f"/teas/{tea_id}")
    assert response.status_code == 404


