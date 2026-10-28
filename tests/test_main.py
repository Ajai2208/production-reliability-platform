from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Production Reliability Platform is running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_orders():
    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert len(data["orders"]) == 3

def test_get_single_order_success():
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "item": "Laptop", "status": "shipped"}

def test_get_single_order_not_found():
    response = client.get("/api/orders/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}
