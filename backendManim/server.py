# server.py (Enhanced Backend with 16:9 Ratio Support)

from flask import Flask, request, jsonify
from flask import send_from_directory
from flask_cors import CORS
import os
import subprocess
import requests
import json
import datetime
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:5]}...") # Print first 5 chars for verification

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Define the project root (where server.py is located)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Directory where Manim code will be saved and videos will be generated
OUTPUT_DIR_RELATIVE = 'generated_animations' 
OUTPUT_DIR_ABSOLUTE = os.path.join(PROJECT_ROOT, OUTPUT_DIR_RELATIVE)

if not os.path.exists(OUTPUT_DIR_ABSOLUTE):
    os.makedirs(OUTPUT_DIR_ABSOLUTE)

# Max retries for Manim command execution
MAX_MANIM_EXECUTION_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# Max retries for AI code generation attempts
MAX_AI_CODE_GENERATION_RETRIES = 3

def log_debug(message: str):
    """Logs a debug message with a timestamp."""
    print(f"[DEBUG] {datetime.datetime.now().isoformat()} - {message}")

def get_manim_code_from_gemini(prompt_text: str) -> str:
    """
    Calls the Gemini API to get enhanced Manim Python code with 16:9 aspect ratio support.
    """
    log_debug("Preparing enhanced prompt for Gemini API...")
    
    system_instruction = """You are an expert Manim Python code generator specializing in creating visually stunning, professional-quality animations.

CRITICAL REQUIREMENTS:
1. ALL animations MUST be designed for 16:9 aspect ratio (1920x1080 or equivalent)
2. Use `config.frame_width` and `config.frame_height` for responsive positioning
3. Center important content and ensure nothing gets cut off at edges

ENHANCED CODING STANDARDS:
- Always start with `from manim import *`
- Create a single class inheriting from `manim.Scene`
- Implement a comprehensive `construct` method
- Use descriptive class names (e.g., `QuantumPhysicsVisualization`, `DataScienceExplanation`)

VISUAL EXCELLENCE:
- Use professional color schemes (consider `BLUE_E`, `RED_E`, `GREEN_E`, `PURPLE_E`, `YELLOW_E`)
- Implement smooth, elegant transitions
- Add appropriate spacing and margins for 16:9 layout
- Use `self.camera.frame.scale()` when needed for better framing

POSITIONING FOR 16:9:
- Horizontal positioning: Use values between -7 and +7 (safe zone: -6 to +6)
- Vertical positioning: Use values between -4 and +4 (safe zone: -3.5 to +3.5)
- For multi-element layouts, use `arrange()` or `arrange_in_grid()` with proper spacing
- Position titles at y=3 to 3.5, main content at y=0, and footnotes at y=-3 to -3.5

ANIMATION BEST PRACTICES:
- Use varied animation types: `Create`, `Write`, `FadeIn`, `FadeOut`, `Transform`, `ReplacementTransform`
- Add appropriate `self.wait()` intervals (0.5-2 seconds typically)
- For continuous animations, use proper updater functions with `(mob, dt)` parameters
- Ensure animations have clear beginnings and endings

MATHEMATICAL CONTENT:
- Use `MathTex` for equations with proper LaTeX syntax
- Use `Text` for regular text with appropriate font sizes
- Ensure mathematical symbols are clearly visible and properly sized

ERROR PREVENTION:
- Handle common Manim errors (missing imports, incorrect syntax, animation conflicts)
- Use try-catch patterns for complex operations when appropriate
- Test positioning with `Dot().move_to()` if uncertain about coordinates

PERFORMANCE OPTIMIZATION:
- Avoid infinite loops or indefinite animations
- Use efficient animation grouping with `AnimationGroup` when beneficial
- Minimize unnecessary object creation

If fixing previous code, analyze the error carefully and provide a complete, corrected solution that addresses the specific issue while maintaining all quality standards.

Generate ONLY the complete Python code without any explanatory text or markdown formatting."""
    
    chat_history = [
        {
            "role": "user",
            "parts": [{"text": f"{system_instruction}\n\nUser request: {prompt_text}"}]
        }
    ]
    
    payload = {
        "contents": chat_history,
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 4096,
        }
    }
    
    log_debug("Sending enhanced request to Gemini API...")
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        log_debug(f"Gemini API response status: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
        log_debug("Gemini API response received successfully.")
        
        if (result.get("candidates") and len(result["candidates"]) > 0 and
            result["candidates"][0].get("content") and
            result["candidates"][0]["content"].get("parts") and
            len(result["candidates"][0]["content"]["parts"]) > 0):
            
            manim_code = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean up the code
            manim_code = clean_generated_code(manim_code)
            
            log_debug(f"Generated Manim code (first 200 chars): {manim_code[:200]}...")
            return manim_code
        else:
            raise Exception("Gemini API response did not contain expected content.")

    except requests.exceptions.RequestException as e:
        log_debug(f"HTTP error while calling Gemini API: {e}")
        raise Exception(f"Failed to connect to AI service: {e}")
    except json.JSONDecodeError:
        log_debug(f"JSON decoding error: {response.text}")
        raise Exception("Invalid response from AI service.")
    except Exception as e:
        log_debug(f"Unexpected error during Gemini API call: {e}")
        raise

def clean_generated_code(code: str) -> str:
    """Clean and enhance the generated Manim code."""
    # Remove markdown code blocks
    if code.startswith("```python"):
        code = code.replace("```python", "").strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    
    # Ensure proper imports
    if "from manim import *" not in code:
        code = "from manim import *\n\n" + code
    
    # Add config for 16:9 if not present
    config_line = "config.pixel_height = 1080\nconfig.pixel_width = 1920\nconfig.frame_rate = 30\n"
    if "config.pixel" not in code:
        # Insert after imports
        lines = code.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not (line.startswith('import') or line.startswith('from')):
                import_end = i
                break
        
        lines.insert(import_end, config_line)
        code = '\n'.join(lines)
    
    return code

def extract_scene_class_name(code: str) -> str:
    """Extract the scene class name from Manim code."""
    # Look for class definition that inherits from Scene
    class_pattern = r'class\s+(\w+)\s*\([^)]*Scene[^)]*\):'
    match = re.search(class_pattern, code)
    
    if match:
        return match.group(1)
    
    # Fallback: look for any class definition
    fallback_pattern = r'class\s+(\w+)\s*\([^)]*\):'
    match = re.search(fallback_pattern, code)
    
    if match:
        return match.group(1)
    
    return "CustomAnimation"

def run_manim_with_retries(file_path: str, scene_name: str, retries: int = MAX_MANIM_EXECUTION_RETRIES) -> tuple:
    """Run Manim command with retry logic."""
    manim_command = [
        "manim",
        "-pqh",  # High quality for better 16:9 output
        "--resolution", "1920,1080",  # Explicit 16:9 resolution
        file_path,
        scene_name
    ]
    
    for attempt in range(retries):
        log_debug(f"Manim execution attempt {attempt + 1}/{retries}")
        
        try:
            process = subprocess.run(
                manim_command, 
                capture_output=True, 
                text=True, 
                cwd=PROJECT_ROOT,
                timeout=120  # 2 minute timeout
            )
            
            if process.returncode == 0:
                log_debug("Manim execution successful")
                return True, None
            else:
                log_debug(f"Manim failed with return code {process.returncode}")
                log_debug(f"STDERR: {process.stderr}")
                
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
                
        except subprocess.TimeoutExpired:
            log_debug(f"Manim execution timed out on attempt {attempt + 1}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY_SECONDS)
            process = type('obj', (object,), {'stderr': 'Manim execution timed out', 'returncode': 1})
    
    return False, process.stderr

@app.route('/generate-manim', methods=['POST'])
def generate_manim_animation():
    log_debug("Received request at /generate-manim")
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        user_id = data.get('user_id')
        chat_id = data.get('chat_id')  # New: chat/session identifier

        if not prompt or not user_id or not chat_id:
            return jsonify({"message": "Prompt, user_id, and chat_id are required"}), 400

        # Fetch last code for this chat_id from Supabase
        previous_code = None
        try:
            response = supabase.table("chats").select("code").eq("chat_id", chat_id).order("timestamp", desc=True).limit(1).execute()
            if response.data and len(response.data) > 0:
                previous_code = response.data[0]["code"]
        except Exception as fetch_error:
            log_debug(f"Supabase fetch error: {fetch_error}")

        manim_execution_failed_stderr = None
        manim_code = None
        MAX_AI_CODE_GENERATION_RETRIES = 3
        file_name = "main.py"  # Always use the same file
        file_path_absolute = os.path.join(OUTPUT_DIR_ABSOLUTE, file_name)
        file_path_relative = os.path.join(OUTPUT_DIR_RELATIVE, file_name)

        for ai_attempt in range(MAX_AI_CODE_GENERATION_RETRIES):
            log_debug(f"AI code generation attempt {ai_attempt + 1}/{MAX_AI_CODE_GENERATION_RETRIES}")
            # Compose prompt for Gemini
            if manim_execution_failed_stderr:
                gemini_prompt = (
                    f"Fix this Manim code for 16:9 aspect ratio based on: {prompt}\n\n"
                    f"Previous code:\n{previous_code}\n\n"
                    f"Error encountered:\n{manim_execution_failed_stderr}\n\n"
                    f"Please provide corrected code that works properly in 16:9 format."
                )
            elif previous_code:
                gemini_prompt = (
                    f"Enhance this Manim code for 16:9 aspect ratio: {prompt}\n\n"
                    f"Previous code to improve:\n{previous_code}\n\n"
                    f"Make it more visually appealing and ensure 16:9 compatibility."
                )
            else:
                gemini_prompt = f"Create a professional 16:9 Manim animation for: {prompt}"

            manim_code = get_manim_code_from_gemini(gemini_prompt)
            with open(file_path_absolute, "w", encoding='utf-8') as f:
                f.write(manim_code)

            scene_name = extract_scene_class_name(manim_code)
            log_debug(f"Detected scene class: {scene_name}")
            success, stderr = run_manim_with_retries(file_path_relative, scene_name)
            if success:
                break
            else:
                manim_execution_failed_stderr = stderr
                log_debug(f"AI attempt {ai_attempt + 1} failed, trying again...")

        if not success:
            return jsonify({
                "message": "Failed to generate animation after multiple attempts",
                "error": manim_execution_failed_stderr,
                "code": manim_code
            }), 500

        # Find the generated video (use fallback dirs as before)
        video_dir = os.path.join(OUTPUT_DIR_ABSOLUTE, "media/videos/main/1080p60")
        fallback_dirs = [
            os.path.join(OUTPUT_DIR_ABSOLUTE, "media/videos/main/1080p30"),
            os.path.join(OUTPUT_DIR_ABSOLUTE, "media/videos/main/720p30"),
            os.path.join(OUTPUT_DIR_ABSOLUTE, "media/videos/main/480p15")
        ]
        video_filename = None
        video_url = None
        if os.path.exists(video_dir):
            video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
            if video_files:
                video_files.sort(key=lambda x: os.path.getmtime(os.path.join(video_dir, x)), reverse=True)
                video_filename = video_files[0]
                video_url = f"/media/main/1080p60/{video_filename}"
        if not video_filename:
            for fallback_dir in fallback_dirs:
                if os.path.exists(fallback_dir):
                    video_files = [f for f in os.listdir(fallback_dir) if f.endswith(".mp4")]
                    if video_files:
                        quality = os.path.basename(fallback_dir)
                        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(fallback_dir, x)), reverse=True)
                        video_filename = video_files[0]
                        video_url = f"/media/main/{quality}/{video_filename}"
                        break

        # Save chat turn to Supabase (with chat_id)
        try:
            supabase.table("chats").insert({
                "user_id": user_id,
                "chat_id": chat_id,
                "prompt": prompt,
                "code": manim_code,
                "video_url": video_url,
                "timestamp": datetime.datetime.now().isoformat()
            }).execute()
        except Exception as db_error:
            log_debug(f"Database insert failed: {db_error}")

        return jsonify({
            "video_url": video_url,
            "code": manim_code,
            "scene_name": scene_name
        })

    except Exception as e:
        log_debug(f"Unexpected error in generate_manim_animation: {e}")
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500

@app.route('/media/<path:filename>')
def serve_video(filename):
    """Serve video files with proper path handling."""
    try:
        # Handle nested paths for different qualities
        media_root = os.path.join(OUTPUT_DIR_ABSOLUTE, "media/videos")
        full_path = os.path.join(media_root, filename)
        
        if os.path.exists(full_path):
            directory = os.path.dirname(full_path)
            file_name = os.path.basename(full_path)
            return send_from_directory(directory, file_name)
        else:
            return jsonify({"message": "Video file not found"}), 404
            
    except Exception as e:
        log_debug(f"Error serving video: {e}")
        return jsonify({"message": "Error serving video"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "output_dir": OUTPUT_DIR_ABSOLUTE
    })

if __name__ == '__main__':
    log_debug("Starting enhanced Flask server on http://localhost:5000")
    log_debug(f"Output directory: {OUTPUT_DIR_ABSOLUTE}")
    app.run(debug=True, port=5000, use_reloader=False)