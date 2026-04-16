from google import genai
import requests

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
# The URL where your main.py server is running
API_URL = "http://127.0.0.1:8000/pay"

# Your specific wallet ID from your database
MY_WALLET = "9c944276-46a8-465a-8d60-20338a232ff1"

# The API Key you generated in Google AI Studio
GEMINI_KEY = "AIzaSyCXRVGzRtO9TgS3ArG67gpHxql21UG9MB4"

# ---------------------------------------------------------
# 2. INITIALIZE THE BRAIN
# ---------------------------------------------------------
# Using the new 2026 Client SDK
client = genai.Client(api_key=GEMINI_KEY.strip())

print("\n" + "="*40)
print("🤖 2026 AI PAYMENT AGENT ONLINE")
print("Status: Connected to Gemini 3 Flash")
print("Commands: 'Pay $5', 'Buy a pizza for 12.50', etc.")
print("="*40 + "\n")

# ---------------------------------------------------------
# 3. MAIN LOOP
# ---------------------------------------------------------
while True:
    user_msg = input("You: ")
    if user_msg.lower() in ["exit", "quit"]: break
    
    try:
        # Using the alias to avoid the 404
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=f"User: {user_msg}. If they want to pay, reply ONLY with the number. Else, say 'CHAT: [msg]'"
        )
        
        ai_reply = response.text.strip()
        print(f"--- DEBUG: Brain says '{ai_reply}' ---")

        # Payment Logic
        if "CHAT" not in ai_reply:
            clean_num = "".join(c for c in ai_reply if c.isdigit() or c == '.')
            if clean_num:
                amount = float(clean_num)
                print(f"Agent: Processing ${amount}...")
                res = requests.post(API_URL, json={"wallet_id": MY_WALLET, "amount": amount})
                print("Server:", res.json())
        else:
            print(f"Agent: {ai_reply.replace('CHAT:', '').strip()}")

    except Exception as e:
        # This will catch if the model name is still a problem
        print(f"Brain connection issue: {e}")
        # The "Money-Maker" Prompt
prompt = (
    f"User: {user_msg}. "
    "If they want to spend money, identify the AMOUNT and the ITEM. "
    "Format: ACTION: PAY, AMOUNT: [number], ITEM: [name]. "
    "If not a payment, just chat."
)

# ... inside your loop ...
if "ACTION: PAY" in ai_reply:
    # Logic to extract data from the AI's response
    amount = float(ai_reply.split("AMOUNT:")[1].split(",")[0].strip())
    item = ai_reply.split("ITEM:")[1].strip()
    
    print(f"💰 Agentpay: Authorized ${amount} for '{item}'.")
    
    # This is where you'd connect to Stripe or a real bank API next
    res = requests.post(API_URL, json={
        "wallet_id": MY_WALLET, 
        "amount": amount,
        "metadata": {"item": item, "status": "completed"}
    })
    print(f"Receipt: {res.json()}")
    import os
from google import genai
import requests

# Use Environment Variables for safety (The "Billionaire" way)
GEMINI_KEY = os.getenv("GEMINI_KEY", "YOUR_KEY_HERE")
API_URL = os.getenv("API_URL", "http://localhost:8000/pay")

client = genai.Client(api_key=GEMINI_KEY)

def handle_user_request(user_input, wallet_id):
    prompt = f"User: {user_input}. If they want to buy/pay, reply: 'PAY: [amount], ITEM: [description]'. Else reply: 'CHAT: [msg]'"
    
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    ai_reply = response.text.strip()

    if "PAY:" in ai_reply:
        # Data Extraction
        try:
            amount = float(ai_reply.split("PAY:")[1].split(",")[0].strip())
            item = ai_reply.split("ITEM:")[1].strip()
            
            # Call your own API
            res = requests.post(API_URL, json={
                "wallet_id": wallet_id,
                "amount": amount,
                "description": item
            })
            return res.json()
        except Exception as e:
            return {"error": str(e)}
    
    return {"message": ai_reply.replace("CHAT:", "").strip()}