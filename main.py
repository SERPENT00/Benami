from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: float
    description: str
    vault_key: str

@app.get("/")
def home():
    return {"status": "Benami Vault Online"}

@app.post("/process_benami_payment")
async def process_payment(request: PaymentRequest):
    return {"status": "Success", "amount": request.amount}
