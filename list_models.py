"""
List ALL models available to current API key using google-genai==2.20.0
Analyzes each Gemini model for suitability
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

print("="*70)
print("Available Models in google-genai==2.20.0")
print("="*70)

try:
    # Create client
    client = genai.Client(api_key=api_key)
    
    # List all models
    print("\nFetching available models...\n")
    models_response = client.models.list()
    models = list(models_response)
    
    if not models:
        print("No models found!")
        exit(1)
    
    print(f"Total models available: {len(models)}\n")
    
    # Filter and analyze Gemini models
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    
    print("="*70)
    print("GEMINI MODELS AVAILABLE")
    print("="*70)
    
    if not gemini_models:
        print("\nNo Gemini models found!")
    else:
        for model in gemini_models:
            print(f"\nModel: {model.name}")
            print(f"  Display Name: {model.display_name}")
            
            # Try to get more details
            if hasattr(model, 'supported_generation_methods'):
                print(f"  Generation Methods: {model.supported_generation_methods}")
            
            if hasattr(model, 'input_token_limit'):
                print(f"  Input Token Limit: {model.input_token_limit}")
            
            if hasattr(model, 'output_token_limit'):
                print(f"  Output Token Limit: {model.output_token_limit}")
            
            # Check for other relevant attributes
            for attr in dir(model):
                if not attr.startswith('_') and attr not in ['name', 'display_name', 'supported_generation_methods', 'input_token_limit', 'output_token_limit']:
                    val = getattr(model, attr, None)
                    if val and not callable(val):
                        print(f"  {attr}: {val}")
    
    print("\n" + "="*70)
    print("ALL MODELS (Complete List)")
    print("="*70 + "\n")
    
    for i, model in enumerate(models, 1):
        print(f"{i}. {model.name}")
        if hasattr(model, 'display_name'):
            print(f"   Display: {model.display_name}")
    
    client.close()
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
