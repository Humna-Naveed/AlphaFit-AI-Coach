"""
Test which Gemini models are actually accessible and suitable for conversational AI coaching
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

# Models to test (focusing on conversational Gemini models)
models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

print("="*70)
print("TESTING MODEL ACCESSIBILITY FOR CONVERSATIONAL AI COACHING")
print("="*70)

client = genai.Client(api_key=api_key)

results = []

for model_name in models_to_test:
    print(f"\nTesting: {model_name}...", end=" ")
    
    try:
        # Try to create a chat
        chat = client.chats.create(
            model=model_name,
            config={"temperature": 1.0}
        )
        
        # Try to send a simple message
        response = chat.send_message("Hello, what is 2+2?")
        
        if response.text:
            print("✓ WORKS")
            results.append({
                "model": model_name,
                "status": "✓ Accessible",
                "chat_support": "Yes",
                "test_response": response.text[:80] + "..." if len(response.text) > 80 else response.text
            })
        else:
            print("✗ No response text")
            results.append({
                "model": model_name,
                "status": "✗ No output",
                "chat_support": "No",
                "test_response": ""
            })
    
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            status = "✗ 404 Not Found"
        elif "permission" in error_msg.lower():
            status = "✗ Permission Denied"
        elif "deprecated" in error_msg.lower():
            status = "✗ Deprecated"
        else:
            status = f"✗ Error: {type(e).__name__}"
        
        print(status)
        results.append({
            "model": model_name,
            "status": status,
            "chat_support": "Unknown",
            "error": error_msg[:150]
        })

print("\n" + "="*70)
print("SUMMARY OF RESULTS")
print("="*70)

working_models = [r for r in results if "✓" in r["status"]]
failed_models = [r for r in results if "✗" in r["status"]]

print(f"\n✓ WORKING MODELS: {len(working_models)}")
for model in working_models:
    print(f"\n  Model: {model['model']}")
    print(f"    Status: {model['status']}")
    print(f"    Chat Support: {model['chat_support']}")
    if "test_response" in model and model["test_response"]:
        print(f"    Test Response: {model['test_response']}")

print(f"\n✗ FAILED MODELS: {len(failed_models)}")
for model in failed_models:
    print(f"\n  Model: {model['model']}")
    print(f"    Status: {model['status']}")
    if "error" in model:
        print(f"    Error: {model['error']}")

client.close()
