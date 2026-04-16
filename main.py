from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI()

# Supabase Setup
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# This defines what a "Payment" looks like
class Payment(BaseModel):
    wallet_id: str
    amount: float

@app.get("/")
def home():
    return {"message": "API is Online"}

@app.post("/pay")
def process_payment(payment: Payment):
    # 1. Get current balance
    res = supabase.table("wallets").select("balance").eq("id", payment.wallet_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    current_balance = res.data[0]["balance"]

    # 2. Check if enough money
    if current_balance < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 3. Update Balance
    new_balance = current_balance - payment.amount
    supabase.table("wallets").update({"balance": new_balance}).eq("id", payment.wallet_id).execute()

    # 4. Record Transaction
    supabase.table("transactions").insert({
        "wallet_id": payment.wallet_id, 
        "amount": payment.amount, 
        "status": "success"
    }).execute()

    return {"status": "SUCCESS", "new_balance": new_balance}

@app.get("/all-transactions")
def show_everything():
    res = supabase.table("transactions").select("*").execute()
    return res.data
import requests

url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key=YOUR_API_KEY"

data = {
    "contents": [
        {
            "parts": [{"text": "Hello"}]
        }
    ]
}

response = requests.post(url, json=data)
print(response.json())
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

# In a real app, this would be a Postgres Database
db = {
    "wallets": {
        "9c944276-46a8-465a-8d60-20338a232ff1": {"balance": 1000.0, "owner": "voldemort"}
    },
    "transactions": []
}

class PaymentRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str

@app.post("/pay")
async def process_payment(req: PaymentRequest):
    if req.wallet_id not in db["wallets"]:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    wallet = db["wallets"][req.wallet_id]
    if wallet["balance"] < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process Transaction
    wallet["balance"] -= req.amount
    tx_id = str(uuid.uuid4())
    db["transactions"].append({"id": tx_id, "amount": req.amount, "item": req.description})
    
    return {"status": "SUCCESS", "tx_id": tx_id, "new_balance": wallet["balance"]}
from fastapi import FastAPI

app = FastAPI(
    title="Benami Agentic Finance",
    description="The anonymous, high-speed payment layer for AI Agents.",
    version="1.0.0"
)
# 1. Make sure you are in the project folder
# 2. Add everything again just to be safe
# 3. Create a "Force Launch" commit
git commit -m "🚀 DEPLOY: Benami Production V1.0"

# 4. Push it to the 'main' branch
git push -u origin main
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "brand": "Benami",
        "status": "Active",
        "message": "The AI Payment Layer is Live."
    }