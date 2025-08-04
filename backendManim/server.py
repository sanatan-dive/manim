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

# Updated Supabase connection with error handling
try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connected successfully")
    else:
        print("Supabase credentials not found, running without database")
        supabase = None
except Exception as e:
    print(f"Supabase connection failed: {e}")
    supabase = None

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:5]}...") # Print first 5 chars for verification

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

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
    
    system_instruction = """You are an expert Manim Python code generator specializing in creating visually stunning, professional-quality animations for 16:9 aspect ratio.

CRITICAL FRAME SPECIFICATIONS:
- Frame dimensions: 1920x1080 pixels (16:9 aspect ratio)
- Manim coordinate system: X-axis [-7.11 to 7.11], Y-axis [-4 to 4]
- SAFE ZONE for content: X[-6 to 6], Y[-3.5 to 3.5]
- NO config lines in your code - they are automatically added

POSITIONING RULES (STRICTLY FOLLOW):
- Titles: y=2.5 to y=3.0 (not higher!)
- Main content: y=-1.0 to y=1.0
- Footer/subscripts: y=-2.5 to y=-3.0
- Use font_size between 24-48 for most text
- Use font_size between 48-72 ONLY for main titles

MANDATORY CODING STRUCTURE:
```python
from manim import *

class YourSceneName(Scene):
    def construct(self):
        # Your animation code here
        pass
```

TEXT SIZING GUIDELINES:
- Title text: Text("Title", font_size=48).move_to(UP * 2.5)
- Regular text: Text("Content", font_size=36).move_to(ORIGIN)
- Math equations: MathTex("x^2", font_size=32)
- Small labels: Text("Label", font_size=24)

ANIMATION QUALITY RULES:
- Use smooth transitions: FadeIn, FadeOut, Create, Write
- Add self.wait(1) between major animations
- Use professional colors: BLUE, RED, GREEN, YELLOW, PURPLE
- Keep animations between 5-15 seconds total
- Ensure all elements fit within the safe zone

FORBIDDEN:
- Do NOT add any config.* lines
- Do NOT use font_size > 72
- Do NOT position elements outside safe zone
- Do NOT create text longer than 40 characters per line

Generate ONLY complete Python code without explanations or markdown."""
    
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
    
    # Retry logic for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60  # Increased timeout to 60 seconds
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

        except requests.exceptions.Timeout as e:
            log_debug(f"Timeout on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retry
                continue
            raise Exception(f"Failed to connect to AI service after {max_retries} attempts: Timeout")
        except requests.exceptions.RequestException as e:
            log_debug(f"HTTP error while calling Gemini API: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Failed to connect to AI service: {e}")
        except json.JSONDecodeError:
            log_debug(f"JSON decoding error: {response.text}")
            raise Exception("Invalid response from AI service.")
        except Exception as e:
            log_debug(f"Unexpected error during Gemini API call: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise

    raise Exception("All retry attempts failed")

def clean_generated_code(code: str) -> str:
    """Clean and enhance the generated Manim code with proper 16:9 configuration."""
    # Remove markdown code blocks
    if code.startswith("```python"):
        code = code.replace("```python", "").strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    
    # Remove any existing config lines
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if not line.strip().startswith('config.'):
            cleaned_lines.append(line)
    
    # Ensure proper imports
    if "from manim import *" not in '\n'.join(cleaned_lines):
        cleaned_lines.insert(0, "from manim import *")
        cleaned_lines.insert(1, "")
    
    # Find where imports end
    import_end = 1
    for i, line in enumerate(cleaned_lines[1:], 1):
        if line.strip() and not (line.startswith('import') or line.startswith('from')):
            import_end = i
            break
    
    # Add comprehensive 16:9 configuration
    config_block = [
        "",
        "# 16:9 Aspect Ratio Configuration", 
        "config.pixel_height = 1080",
        "config.pixel_width = 1920",
        "config.frame_rate = 30",
        "config.background_color = BLACK",
        ""
    ]
    
    # Insert config after imports
    for i, config_line in enumerate(config_block):
        cleaned_lines.insert(import_end + i, config_line)
    
    final_code = '\n'.join(cleaned_lines)
    
    # Validate and fix common positioning issues
    final_code = fix_positioning_issues(final_code)
    
    return final_code

def fix_positioning_issues(code: str) -> str:
    """Fix common positioning issues that cause out-of-frame content."""
    
    # Fix overly large font sizes
    code = re.sub(r'font_size=(\d+)', lambda m: f'font_size={min(int(m.group(1)), 48)}' if int(m.group(1)) > 48 else m.group(0), code)
    
    # Fix positioning that's too high/low
    code = re.sub(r'UP \* (\d+\.?\d*)', lambda m: f'UP * {min(float(m.group(1)), 3.0)}', code)
    code = re.sub(r'DOWN \* (\d+\.?\d*)', lambda m: f'DOWN * {min(float(m.group(1)), 3.0)}', code)
    
    # Fix positioning that's too far left/right
    code = re.sub(r'LEFT \* (\d+\.?\d*)', lambda m: f'LEFT * {min(float(m.group(1)), 6.0)}', code)
    code = re.sub(r'RIGHT \* (\d+\.?\d*)', lambda m: f'RIGHT * {min(float(m.group(1)), 6.0)}', code)
    
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
    """Run Manim command with retry logic and proper 16:9 settings."""
    manim_command = [
        "manim",
        "-pqh",  # High quality
        "--resolution", "1920,1080",  # Explicit 16:9 resolution
        "--format", "mp4",
        file_path,
        scene_name
    ]
    
    for attempt in range(retries):
        log_debug(f"Manim execution attempt {attempt + 1}/{retries}")
        log_debug(f"Command: {' '.join(manim_command)}")
        
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
                log_debug(f"STDOUT: {process.stdout}")
                
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
        chat_id = data.get('chat_id')

        if not prompt or not user_id or not chat_id:
            return jsonify({"message": "Prompt, user_id, and chat_id are required"}), 400

        # Fetch last code for this chat_id from Supabase
        previous_code = None
        if supabase:
            try:
                response = supabase.table("chats").select("code").eq("chat_id", chat_id).order("timestamp", desc=True).limit(1).execute()
                if response.data and len(response.data) > 0:
                    previous_code = response.data[0]["code"]
                    log_debug(f"Found previous code for chat_id {chat_id}")
                else:
                    log_debug(f"No previous code found for chat_id {chat_id}, starting new chat")
            except Exception as fetch_error:
                log_debug(f"Supabase fetch error: {fetch_error}")
        else:
            log_debug("No Supabase connection, skipping history fetch")

        manim_execution_failed_stderr = None
        manim_code = None
        file_name = "main.py"
        file_path_absolute = os.path.join(OUTPUT_DIR_ABSOLUTE, file_name)
        file_path_relative = os.path.join(OUTPUT_DIR_RELATIVE, file_name)

        for ai_attempt in range(MAX_AI_CODE_GENERATION_RETRIES):
            log_debug(f"AI code generation attempt {ai_attempt + 1}/{MAX_AI_CODE_GENERATION_RETRIES}")
            
            # Enhanced prompt composition
            if manim_execution_failed_stderr:
                gemini_prompt = (
                    f"FIX POSITIONING ERROR - Create 16:9 Manim animation: {prompt}\n\n"
                    f"Previous failing code:\n{manim_code if manim_code else previous_code}\n\n"
                    f"Error:\n{manim_execution_failed_stderr}\n\n"
                    f"REQUIREMENTS:\n"
                    f"- Keep ALL text within safe zone: X[-6,6], Y[-3.5,3.5]\n"
                    f"- Use font_size <= 48\n"
                    f"- Position titles at y=2.5 maximum\n"
                    f"- Fix the positioning error and ensure visibility"
                )
            elif previous_code:
                gemini_prompt = (
                    f"ENHANCE 16:9 Manim animation: {prompt}\n\n"
                    f"Previous code:\n{previous_code}\n\n"
                    f"REQUIREMENTS:\n"
                    f"- Improve visuals while keeping within frame bounds\n"
                    f"- Safe zone: X[-6,6], Y[-3.5,3.5]\n"
                    f"- Use appropriate font sizes (24-48)"
                )
            else:
                gemini_prompt = (
                    f"CREATE 16:9 Manim animation: {prompt}\n\n"
                    f"CRITICAL REQUIREMENTS:\n"
                    f"- ALL content must fit in 16:9 frame\n"
                    f"- Safe positioning: X[-6,6], Y[-3.5,3.5]\n"
                    f"- Proper font sizes: 24-48 for most text\n"
                    f"- Professional appearance with smooth animations"
                )

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

        # Find the generated video
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

        # Save to Supabase
        if supabase:
            try:
                supabase.table("chats").insert({
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "prompt": prompt,
                    "code": manim_code,
                    "video_url": video_url,
                    "timestamp": datetime.datetime.now().isoformat()
                }).execute()
                log_debug("Chat turn saved to Supabase successfully")
            except Exception as db_error:
                log_debug(f"Database insert failed: {db_error}")
        else:
            log_debug("No Supabase connection, skipping database save")

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