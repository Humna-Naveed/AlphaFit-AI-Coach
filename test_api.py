"""Test script to inspect google.genai API"""
import google.genai as genai

print("="*60)
print("Inspecting google.genai API")
print("="*60)

# Get main classes and functions
public_items = [x for x in dir(genai) if not x.startswith('_')]
print("\nPublic classes and functions:")
for item in public_items:
    obj = getattr(genai, item)
    print(f"  - {item}: {type(obj).__name__}")

# Check for specific key classes
print("\nChecking for key classes:")
print(f"  - GenerativeModel: {'GenerativeModel' in dir(genai)}")
print(f"  - Client: {'Client' in dir(genai)}")
print(f"  - AsyncClient: {'AsyncClient' in dir(genai)}")

# Try to see the GenerativeModel class if it exists
if hasattr(genai, 'GenerativeModel'):
    print("\nGenerativeModel methods:")
    gm = genai.GenerativeModel
    methods = [x for x in dir(gm) if not x.startswith('_')]
    for method in methods[:10]:  # First 10
        print(f"  - {method}")
