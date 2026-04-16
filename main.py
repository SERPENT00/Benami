from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Benami Secure API")

# 1. SECURITY CONFIG
# This looks for the BENAMI_API_KEY you set in Render's Environment Variables
API_KEY = os.getenv("BENAMI_API_KEY")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(status_code=403, detail="Unauthorized: Invalid Vault Key")

# 2. SUPABASE CONNECTION
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_KEY")
)

class PaymentRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str

@app.get("/")
def health_check():
    return {"status": "Active", "vault": "Locked & Secure"}

@app.post("/pay")
async def process_payment(req: PaymentRequest, token: str = Depends(verify_key)):
    # A. Check if the wallet exists and get current balance
    wallet = supabase.table("wallets").select("balance").eq("id", req.wallet_id).single().execute()
    
    if not wallet.data:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    current_balance = float(wallet.data["balance"])

    # B. Check for sufficient funds
    if current_balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in Benami vault")

    # C. Perform the transaction (Subtract money)
    new_balance = current_balance - req.amount
    supabase.table("wallets").update({"balance": new_balance}).eq("id", req.wallet_id).execute()
    
    # D. Log the transaction for your billionaire audit trail
    supabase.table("transactions").insert({
        "wallet_id": req.wallet_id,
        "amount": req.amount,
        "description": req.description
    }).execute()

    return {
        "status": "SUCCESS",
        "paid_amount": req.amount,
        "remaining_balance": new_balance,
        "note": req.description
    }