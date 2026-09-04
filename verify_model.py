"""
Minimal real API test for gemini-2.5-flash
Tests actual model accessibility with user's API key
"""
import os
from dotenv import load_dotenv
import google.genai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

print("="*60)
print("Testing gemini-2.5-flash Accessibility")
print("="*60)

try:
    print("\n1. Creating client...")
    client = genai.Client(api_key=api_key)
    print("   ✓ Client created")
    
    print("\n2. Creating chat with gemini-2.5-flash...")
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={"temperature": 1.0}
    )
    print("   ✓ Chat created")
    
    print("\n3. Sending test message...")
    response = chat.send_message("What is 2+2?")
    print("   ✓ Response received")
    
    print("\n4. Response text:")
    print(f"   {response.text}")
    
    print("\n" + "="*60)
    print("✓ SUCCESS: gemini-2.5-flash is accessible!")
    print("="*60)
    
    client.close()
    
except Exception as e:
    print("\n" + "="*60)
    print("✗ FAILURE: Error accessing gemini-2.5-flash")
    print("="*60)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    import traceback
    traceback.print_exc()
