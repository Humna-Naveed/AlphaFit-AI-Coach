"""Minimal test to understand google-genai 2.20.0 API"""
import os
from dotenv import load_dotenv
import google.genai as genai

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create client with the google-genai 2.x API.
client = genai.Client(api_key=api_key)

print("Client created successfully")
print(f"Client type: {type(client)}")
print(f"Client.chats type: {type(client.chats)}")

# Try to create a chat
print("\n" + "="*60)
print("Attempting to create a chat...")
print("="*60)

try:
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={
            "temperature": 1
        }
    )
    print(f"Chat created: {chat}")
    print(f"Chat type: {type(chat)}")
    print(f"Chat methods: {[x for x in dir(chat) if not x.startswith('_')]}")
    
    # Try to send a message
    print("\nSending test message...")
    response = chat.send_message("Hello, what is 2+2?")
    print(f"Response type: {type(response)}")
    print(f"Response.text: {response.text if hasattr(response, 'text') else 'no text attr'}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
