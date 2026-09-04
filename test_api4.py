"""Test creating and using a Chat in google-genai 2.20.0"""
import google.genai as genai
import inspect

print("="*60)
print("Google-genai 2.20.0 - Chat Creation and Usage")
print("="*60)

# Check Client.chats attribute
Client = genai.Client
print("\nClient.chats type:")
print(f"  {type(Client.chats)}")

# Get chats attribute methods
chats_class = type(Client.chats.fget(None)) if hasattr(Client.chats, 'fget') else None

# Let's check the chats module directly
from google.genai import chats as chats_module
print("\nChats module classes:")
chats_classes = [x for x in dir(chats_module) if x[0].isupper() and not x.startswith('_')]
print(f"  {chats_classes}")

# Check Chats class (plural)
if hasattr(chats_module, 'Chats'):
    Chats = chats_module.Chats
    print("\nChats class (plural) methods:")
    methods = [x for x in dir(Chats) if not x.startswith('_')]
    for method in sorted(methods):
        if callable(getattr(Chats, method)):
            try:
                sig = inspect.signature(getattr(Chats, method))
                print(f"  - {method}{sig}")
            except:
                print(f"  - {method}")

# Check AsyncChats class
if hasattr(chats_module, 'AsyncChats'):
    print("\nAsyncChats class exists")
