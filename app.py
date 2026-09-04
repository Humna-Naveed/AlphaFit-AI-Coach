"""
AlphaFit AI Coach - Phase 1: Standalone Python Application
Connects to Gemini API for fitness and nutrition guidance.
Uses google-genai 2.20.0 SDK (NOT the older google-generativeai).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

# Retrieve API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file. "
        "Please add your API key to .env"
    )

# Model to use (must be available in your Google AI account)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def load_system_prompt(filepath: str) -> str:
    """Load the system prompt from a text file."""
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"System prompt file not found: {filepath}")


def main():
    """Main function to run the AlphaFit AI Coach chatbot."""
    
    # Load system prompt
    system_prompt = load_system_prompt(str(PROJECT_ROOT / "prompts" / "system_prompt.txt"))
    
    # Create client with API key
    # google-genai 2.x receives the key when the client is constructed.
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Create chat session with system prompt
    # The config dict allows us to pass system instructions
    chat = client.chats.create(
        model=MODEL_NAME,
        config={
            "system_instruction": system_prompt,
            "temperature": 1.0
        }
    )
    
    print("\n" + "="*60)
    print("AlphaFit AI Coach")
    print("="*60)
    print("Type your fitness/nutrition questions below.")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nAlphaFit: Thank you for using AlphaFit AI Coach! Stay healthy! 💪")
                break
            
            # Skip empty input
            if not user_input:
                print("AlphaFit: Please enter a message.\n")
                continue
            
            try:
                # Send message to Gemini and get response
                # The chat automatically maintains conversation history
                response = chat.send_message(user_input)
                ai_response = response.text
                
                print(f"\nAlphaFit: {ai_response}\n")
                
            except Exception as e:
                print("\nError: Failed to get response from Gemini API. Please try again.\n")
    
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
