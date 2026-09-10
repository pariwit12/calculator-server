from fastapi.testclient import TestClient
from main import app  # or whatever your app module is

import pytest
from main import history

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_history_before_each_test():
    """ล้างประวัติก่อนรันแต่ละ test เพื่อป้องกันผลกระทบข้าม test case"""
    history.clear()

def test_basic_division():
    r = client.post("/calculate", params={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", params={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", params={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", params={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

def test_empty_expr_returns_ok_false():
    """ทดสอบกรณีส่ง String ว่างเปล่า (อัปเดตตามโค้ดใหม่)"""
    r = client.post("/calculate", params={"expr": "   "})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert data["error"] == "Expression cannot be empty"

# TODO Add more tests
# --- GET /history Tests (3 Cases) ---
def test_get_history_empty():
    """Case 1: ดึง history เมื่อยังไม่มีข้อมูล"""
    r = client.get("/history")
    assert r.status_code == 200
    data = r.json()
    # โค้ดใหม่คืนค่าเป็น List โดยตรง
    assert isinstance(data, list)
    assert data == []

def test_get_history_after_calculations():
    """Case 2: ดึง history หลังจากการคำนวณหลายครั้ง"""
    client.post("/calculate", params={"expr": "10+5"})
    client.post("/calculate", params={"expr": "4*2"})
    
    r = client.get("/history")
    assert r.status_code == 200
    data = r.json()
    
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["expr"] == "10+5"
    assert "timestamp" in data[0]  # เช็คว่ามีฟิลด์ timestamp
    assert data[1]["expr"] == "4*2"

def test_get_history_with_limit_query():
    """Case 3: ดึง history โดยใช้ query parameter 'limit'"""
    client.post("/calculate", params={"expr": "1+1"})
    client.post("/calculate", params={"expr": "2+2"})
    client.post("/calculate", params={"expr": "3+3"})
    
    # ดึงค่า 2 รายการล่าสุด (ตามเงื่อนไข items[-limit:])
    r = client.get("/history", params={"limit": 2})
    assert r.status_code == 200
    data = r.json()
    
    assert isinstance(data, list)
    assert len(data) == 2
    # ค่าล่าสุด 2 อันต้องเป็น 2+2 และ 3+3 ตามลำดับ
    assert data[0]["expr"] == "2+2"
    assert data[1]["expr"] == "3+3"

# --- DELETE /history Tests (3 Cases) ---
def test_delete_history_success_status():
    """Case 1: ลบ history และตรวจสอบ status code กับ response"""
    client.post("/calculate", params={"expr": "5+5"})
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "cleared" in data["message"].lower()

def test_delete_history_clears_all_records():
    """Case 2: ตรวจสอบว่าหลังจาก DELETE แล้ว ข้อมูลใน GET /history ว่างเปล่าจริง"""
    client.post("/calculate", params={"expr": "100/2"})
    client.post("/calculate", params={"expr": "50-10"})
    
    client.delete("/history")
    
    r = client.get("/history")
    assert r.status_code == 200
    # ตรวจสอบกับ List ว่าง
    # assert r.json()["history"] == []
    assert r.json() == []

def test_delete_history_when_already_empty():
    """Case 3: ลบ history เมื่อประวัติว่างเปล่าอยู่แล้ว (ต้องไม่พัง)"""
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True