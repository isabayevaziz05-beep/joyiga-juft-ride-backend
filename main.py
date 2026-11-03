from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="JUFT RIDE API",
    description="Yo‘lovchi narx belgilaydigan taksi platformasi backend qismi",
    version="1.0.0"
)

# Ma'lumotlar modellari (Pydantic yordamida tekshiriladi)
class OrderCreate(BaseModel):
    passenger_id: str
    pickup_location: str
    dropoff_location: str
    offered_price: int  # Masalan: 40000 (so'm)

class OrderResponse(BaseModel):
    order_id: int
    passenger_id: str
    pickup_location: str
    dropoff_location: str
    offered_price: int
    status: str

class DriverAccept(BaseModel):
    driver_id: str
    order_id: int

# Vaqtinchalik xotiradagi baza (ma'lumotlarni saqlash uchun)
fake_orders_db = []
order_id_counter = 1

@app.get("/")
def home():
    return {"message": "JUFT RIDE API ishga tushdi! Xush kelibsiz."}

# 1. Yo'lovchi tomonidan buyurtma yaratish (Narx taklif qilish)
@app.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate):
    global order_id_counter
    
    new_order = {
        "order_id": order_id_counter,
        "passenger_id": order.passenger_id,
        "pickup_location": order.pickup_location,
        "dropoff_location": order.dropoff_location,
        "offered_price": order.offered_price,
        "status": "searching" # searching, accepted, completed
    }
    
    fake_orders_db.append(new_order)
    order_id_counter += 1
    
    return new_order

# 2. Haydovchilar uchun faol buyurtmalar ro'yxatini ko'rsatish
@app.get("/orders/active", response_model=List[OrderResponse])
def get_active_orders():
    active_orders = [o for o in fake_orders_db if o["status"] == "searching"]
    return active_orders

# 3. Haydovchining buyurtmani qabul qilishi
@app.post("/orders/accept")
def accept_order(data: DriverAccept):
    for order in fake_orders_db:
        if order["order_id"] == data.order_id:
            if order["status"] != "searching":
                raise HTTPException(status_code=400, detail="Bu buyurtma allaqachon olingan yoki bekor qilingan!")
            
            order["status"] = "accepted"
            order["driver_id"] = data.driver_id
            return {
                "message": "Buyurtma muvaffaqiyatli qabul qilindi!",
                "order": order
            }
            
    raise HTTPException(status_code=404, detail="Buyurtma topilmadi!")
