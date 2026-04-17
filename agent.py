import requests
from google import genai
from google.genai import types

# ==========================================
# 1. YOUR SECURE CREDENTIALS (CONNECTED)
# ==========================================
# WARNING: If this key gives a 403 error, generate a new one in AI Studio.
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WALLET_ID = "9c944276-46a8-465a-8d60-20338a232ff1"

# Must match the BENAMI_API_KEY in your Render environment settings
VAULT_KEY = "Serpent@62"
RENDER_URL = "https://benami.onrender.com"

# ==========================================
# 2. THE PAYMENT TOOL
# ==========================================
def process_benami_payment(amount: float, description: str):
    """Securely triggers a payment on the Benami Layer."""
    headers = {
        "access_token": VAULT_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "wallet_id": WALLET_ID,
        "amount": amount,
        "description": description
    }
    
    print(f"\n[SYSTEM] AI is initiating payment of ${amount} for: {description}")
    
    try:
        response = requests.post(f"{RENDER_URL}/pay", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            # Note: Ensure your main.py returns 'remaining_balance' or 'new_balance'
            print(f"[SYSTEM] Success! Transaction complete.")
            return result
        else:
            print(f"[SYSTEM] Failed: {response.text}")
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. INITIALIZE & RUN
# ==========================================
client = genai.Client(api_key=GEMINI_API_KEY)

# UPDATED: gemini-1.5-flash is retired. Use 2.0-flash.
MODEL_ID = MODEL_ID = "gemini-3-flash-preview"
def main():
    prompt = "Use the Benami tool to pay $25.00 for a high-priority server recharge now."
    
    print("🤖 AI is starting...")
    
    try:
        # This is the SDK call that tells Gemini to use your payment function
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[process_benami_payment],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )
        )
        print(f"\n🤖 AI Final Response: {response.text}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()