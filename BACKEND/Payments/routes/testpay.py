from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
import uuid
import os

# === DATABASE SETUP ===
DATABASE_URL = "sqlite:///./pesapal.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"
    transaction_id = Column(String, primary_key=True, index=True)
    email = Column(String)
    amount = Column(Float)
    currency = Column(String)
    payment_method = Column(String)
    status = Column(String)

Base.metadata.create_all(bind=engine)

# === FASTAPI SETUP ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# === PESAPAL CONFIG ===
PESAPAL_CONSUMER_KEY = "TDpigBOOhs+zAl8cwH2Fl82jJGyD8xev"
PESAPAL_CONSUMER_SECRET = "1KpqkfsMaihIcOlhnBo/gBZ5smw="
AUTH_URL = " https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
PAYMENT_URL = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"

def get_pesapal_token():
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"consumer_key": PESAPAL_CONSUMER_KEY, "consumer_secret": PESAPAL_CONSUMER_SECRET}
    response = requests.post(AUTH_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    raise HTTPException(status_code=400, detail="Failed to authenticate with Pesapal")

@app.post("/pesapal/pay")
async def initiate_payment(request: Request):
    data = await request.json()
    plan = data.get("plan")
    amount = data.get("amount")

    if not plan or not amount:
        raise HTTPException(status_code=400, detail="Missing plan or amount")

    token = get_pesapal_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    order_id = "order-" + str(uuid.uuid4())
    order_data = {
        "id": order_id,
        "amount": str(amount),
        "currency": "USD",
        "description": f"Payment for plan {plan}",
        "notification_id": "77ab9602-7201-43bb-bf95-dbb18ada00a4",  # Replace with real ID
        "callback_url": "https://28f0-93-190-140-103.ngrok/response-page",  # Replace
        "redirect_mode": "GET",
        "billing_address": {
            "email_address": "john.doe@example.com",
            "phone_number": "0723xxxxxx",
            "country_code": "KE",
            "first_name": "John",
            "middle_name": "",
            "last_name": "Doe",
            "line_1": "Pesapal Limited",
            "city": "Nairobi",
            "state": "",
            "postal_code": "",
            "zip_code": ""
        }
    }

    response = requests.post(PAYMENT_URL, json=order_data, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Save payment in database
        db = SessionLocal()
        payment = Payment(
            transaction_id=order_id,
            email="john.doe@example.com",
            amount=float(amount),
            currency="USD",
            payment_method="unknown",
            status="initiated"
        )
        db.add(payment)
        db.commit()
        db.close()

        return data

    raise HTTPException(status_code=500, detail=f"Payment failed: {response.text}")

# === ADMIN DATA API ===
@app.get("/admin/payments/")
def get_all_payments():
    db = SessionLocal()
    payments = db.query(Payment).all()
    db.close()

    result = [
        {
            "transaction_id": p.transaction_id,
            "email": p.email,
            "amount": p.amount,
            "currency": p.currency,
            "payment_method": p.payment_method,
            "status": p.status
        }
        for p in payments
    ]
    return {"payments": result}

# === SERVE HTML ADMIN PAGE ===
@app.get("/admin", response_class=HTMLResponse)
def get_admin_page():
    return FileResponse("adminPanel.html")  # <- Save your HTML here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)