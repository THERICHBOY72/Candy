from fastapi import FastAPI
from DataBase.database import create_user, authenticate_user
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8000"],
    allow_credentials = True,
    allow_methods = ["GET", "POST", "DELETE"],
    allow_header = ["Content-Type", "Authorization"],
)

class User(BaseModel):
    username: str
    password: str
    email: str

@app.post("/register/")
def register_user(user: User):
    """
    Register a new user with username, password, and email.
    """
    create_user(user.username, user.password, user.email)
    return {"message": "User registered successfully"}

@app.post("/login/")
def login_user(user: User):
    session_token = authenticate_user(user.email, user.password)
    
    if session_token:
        return {"message": "Login successful", "session_token": session_token}
    else:   
        return {"message": "Invalid email or password"}, 401
    

@app.get("/admin/payments/filter/")
def filter_payments(status:str): 
    conn = sqlite3.connect("forex_academy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE status = ?", (status,))
    payments = cursor.fetchall()
    conn.close()

    return {"payments": [dict(zip(["transaction_id", "email", "amount", "currency", "payment_method", "status"],payment)) for payment in payments]}    
