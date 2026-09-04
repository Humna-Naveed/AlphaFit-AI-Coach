"""Inspect google.genai Client API"""
import google.genai as genai
import inspect

print("="*60)
print("Google-genai 2.20.0 Client API")
print("="*60)

# Get Client class
Client = genai.Client

print("\nClient class constructor:")
print(inspect.signature(Client.__init__))

print("\nClient public methods:")
methods = [x for x in dir(Client) if not x.startswith('_') and callable(getattr(Client, x))]
for method in sorted(methods):
    print(f"  - {method}")

# Check models
print("\n\nChecking 'models' submodule:")
if hasattr(genai, 'models'):
    models = genai.models
    print(f"  Available: {dir(models)}")

# Check chats
print("\nChecking 'chats' submodule:")
if hasattr(genai, 'chats'):
    chats = genai.chats
    print(f"  Available: {[x for x in dir(chats) if not x.startswith('_')]}")
