"""Test google-genai 2.20.0 API - Multi-turn conversation"""
import google.genai as genai
from google.genai.chats import Chat
import inspect

print("="*60)
print("Testing google-genai 2.20.0 Chat API")
print("="*60)

# Check Chat class
print("\nChat class info:")
print(f"Chat class: {Chat}")

print("\nChat class constructor signature:")
try:
    sig = inspect.signature(Chat.__init__)
    print(f"  {sig}")
except Exception as e:
    print(f"  Error: {e}")

print("\nChat class methods:")
methods = [x for x in dir(Chat) if not x.startswith('_') and callable(getattr(Chat, x))]
for method in sorted(methods):
    try:
        sig = inspect.signature(getattr(Chat, method))
        print(f"  - {method}{sig}")
    except Exception as e:
        print(f"  - {method}: (could not get signature)")

# Check genai.Client.chats
print("\n\nChecking if Client has 'chats' attribute:")
Client = genai.Client
client_methods = [x for x in dir(Client) if 'chat' in x.lower()]
print(f"  Methods with 'chat': {client_methods}")
