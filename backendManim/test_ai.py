import os
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

load_dotenv()

# Import config from the top level config.py which is in path
try:
    from config import settings
except ImportError:
    # Fallback if running from wrong dir or something
    print("Could not import settings from config")
    sys.exit(1)

from app.services.ai_service import generate_code

def test_generation():
    print(f"Testing with model: {settings.MODEL_NAME}")
    prompt = "Create a simple Manim animation of a circle transforming into a square."
    
    try:
        print("Sending request to Google Gemini...")
        code = generate_code(prompt)
        print("\n✅ Generation Successful!")
        print("Generated Code Snippet:")
        print(code[:200] + "...")
    except Exception as e:
        print(f"\n❌ Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
