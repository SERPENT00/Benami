from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv

# Load environment variables for later use with Supabase/Gemini
load_dotenv()

# 1. Initialize the App with Branding
app = FastAPI(
    title="Benami Agentic Finance",
    description="The anonymous, high-speed payment layer for AI Agents.",
    version="1.0.0"
)

# 2. Mock Database (Replace with Supabase URL/Key later)
db = {
    "wallets": {
        "9c944276-46a8-465a-8d60-20338a232ff1": {"balance": 1000.0, "owner": "voldemort"}
    },
    "transactions": []
}

# 3. Data Models
class PaymentRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str

# 4. API Routes
@app.get("/")
def read_root():
    """Welcome screen to prevent the blank page error."""
    return {
        "brand": "Benami",
        "status": "Active",
        "message": "The AI Payment Layer is Live.",
        "documentation": "/docs"
    }

@app.post("/pay")
async def process_payment(req: PaymentRequest):
    """The core engine: deducts funds and records the transaction."""
    if req.wallet_id not in db["wallets"]:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    wallet = db["wallets"][req.wallet_id]
    if wallet["balance"] < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Execute Transaction
    wallet["balance"] -= req.amount
    tx_id = str(uuid.uuid4())
    
    transaction_record = {
        "id": tx_id, 
        "amount": req.amount, 
        "description": req.description,
        "status": "SUCCESS"
    }
    
    db["transactions"].append(transaction_record)
    
    return {
        "status": "SUCCESS", 
        "tx_id": tx_id, 
        "new_balance": wallet["balance"]
    }

@app.get("/history")
def get_history():
    """View all processed payments."""
    return db["transactions"]