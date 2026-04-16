from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Benami Permanent Layer")

# Supabase Connection
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class PaymentRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str

@app.get("/")
def home():
    return {"status": "Permanent Memory Active"}

@app.post("/pay")
async def process_payment(req: PaymentRequest):
    # 1. Fetch real balance from Supabase
    wallet_query = supabase.table("wallets").select("balance").eq("id", req.wallet_id).single().execute()
    
    if not wallet_query.data:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    current_balance = wallet_query.data["balance"]

    # 2. Check funds
    if current_balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 3. Update Balance in Database
    new_balance = float(current_balance) - req.amount
    supabase.table("wallets").update({"balance": new_balance}).eq("id", req.wallet_id).execute()

    # 4. Record Transaction permanently
    supabase.table("transactions").insert({
        "wallet_id": req.wallet_id,
        "amount": req.amount,
        "description": req.description
    }).execute()

    return {"status": "SUCCESS", "new_balance": new_balance}