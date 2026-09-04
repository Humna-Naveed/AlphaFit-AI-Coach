"""Correct google-genai 2.20.0 API test"""
import os
from dotenv import load_dotenv
import google.genai as genai

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("Creating client with API key...")

# Create the client with the google-genai 2.x API.
client = genai.Client(api_key=api_key)

print("Client created successfully")
print(f"Client type: {type(client)}")

# Try to create a chat
print("\n" + "="*60)
print("Creating a chat...")
print("="*60)

try:
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={
            "temperature": 1
        }
    )
    print(f"✓ Chat created successfully")
    print(f"  Chat type: {type(chat)}")
    
    # Try to send a message
    print("\n" + "="*60)
    print("Sending test message...")
    print("="*60)
    response = chat.send_message("Hello! What is 2+2?")
    print(f"✓ Got response")
    print(f"  Response type: {type(response)}")
    print(f"  Has .text: {hasattr(response, 'text')}")
    if hasattr(response, 'text'):
        print(f"  Response.text: {response.text[:100]}...")
    
    # Try another message (testing conversation history)
    print("\n" + "="*60)
    print("Sending follow-up message...")
    print("="*60)
    response2 = chat.send_message("Can you explain that?")
    print(f"✓ Got follow-up response")
    if hasattr(response2, 'text'):
        print(f"  Response.text: {response2.text[:100]}...")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
