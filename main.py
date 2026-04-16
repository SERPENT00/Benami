from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Benami Secure API v1.0")

# 1. Security Config
API_KEY = os.getenv("BENAMI_API_KEY") # You will set this in Render
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(status_code=403, detail="Unauthorized: Invalid Benami Key")

# 2. Supabase Setup
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class PaymentRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str

@app.get("/")
def home():
    return {"status": "Secure", "vault": "Locked"}

@app.post("/pay")
async def process_payment(req: PaymentRequest, token: str = Depends(get_api_key)):
    # Fetch Balance
    res = supabase.table("wallets").select("balance").eq("id", req.wallet_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    current_balance = float(res.data["balance"])

    if current_balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Transaction Logic
    new_balance = current_balance - req.amount
    supabase.table("wallets").update({"balance": new_balance}).eq("id", req.wallet_id).execute()
    
    supabase.table("transactions").insert({
        "wallet_id": req.wallet_id,
        "amount": req.amount,
        "description": req.description
    }).execute()

    return {"status": "SUCCESS", "new_balance": new_balance}