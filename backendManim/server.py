# server.py (Conceptual Backend)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Added for Cross-Origin Resource Sharing
import os
import subprocess
import requests # Used for making HTTP requests to Gemini API
import json 
import datetime # Added for logging timestamps
import time # Added for retry delay
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Configuration ---
# Replace with your actual Gemini API key
# It's highly recommended to load this from environment variables in a real app
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:5]}...") # Print first 5 chars for verification, hide rest for security

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Define the project root (where server.py is located)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Directory where Manim code will be saved and videos will be generated
# This path is relative to PROJECT_ROOT
OUTPUT_DIR_RELATIVE = 'generated_animations' 
OUTPUT_DIR_ABSOLUTE = os.path.join(PROJECT_ROOT, OUTPUT_DIR_RELATIVE)

if not os.path.exists(OUTPUT_DIR_ABSOLUTE):
    os.makedirs(OUTPUT_DIR_ABSOLUTE)

# Max retries for Manim command execution
MAX_MANIM_EXECUTION_RETRIES = 2 # Retries for the subprocess.run Manim command
RETRY_DELAY_SECONDS = 2

# Max retries for AI code generation attempts (if Manim execution consistently fails)
MAX_AI_CODE_GENERATION_RETRIES = 2 

def log_debug(message: str):
    """
    Logs a debug message with a timestamp.
    """
    print(f"[DEBUG] {datetime.datetime.now().isoformat()} - {message}")

# --- Helper Function to Call Gemini API ---
def get_manim_code_from_gemini(prompt_text: str) -> str:
    """
    Calls the Gemini API to get Manim Python code based on the prompt.
    """
    log_debug("Preparing prompt for Gemini API...")
    
    system_instruction = (
        "You are an expert Manim Python code generator. "
        "Your task is to generate complete, runnable Python code for a Manim animation "
        "based on the user's request. "
        "The code must define a single class that inherits from `manim.Scene` and "
        "implement a `construct` method. "
        "Always include `from manim import *` at the very top. "
        "The animation should be visually clear, concise, and effectively explain the concept. "
        "Use standard Manim Mobjects such as `Circle`, `Square`, `Text`, `MathTex`, `Axes`, `Line`, `Arrow`, `Dot`. "
        "Animate using `self.play()` with common animations like `Create`, `Transform`, `FadeIn`, `FadeOut`, `Write`, `MoveTo`, `Rotate`. "
        "Control animation timing with `self.wait()`. "
        "Choose a descriptive and valid Python class name for the scene (e.g., `SineWaveScene`, `PythagoreanTheoremAnimation`, `BouncingBallSimulation`). "
        "If an animation involves continuous updates (e.g., a moving object), use `add_updater` and ensure the updater function accepts both `mob` (the mobject being updated) and `dt` (delta time) as arguments, like `def update_function(mob, dt): ...`. "
        "Do NOT include any Manim CLI commands (e.g., `manim -pql`), external file operations (e.g., `open()`, `read()`, `write()`), "
        "or complex system interactions. "
        "The generated code must be entirely self-contained within the `construct` method and rely only on Manim and standard Python libraries (like `math` or `numpy` if imported). "
        "Avoid infinite loops or animations that run indefinitely without a clear end. "
        "If a previous Manim execution error is provided, analyze it carefully and generate revised Manim code that attempts to fix the issue. Focus on common Manim errors such as missing imports, incorrect Mobject usage, improper animation calls, or issues with `MathTex` syntax. "
        "Provide ONLY the complete Python code for the Manim scene, without any conversational text or explanations outside the code block."
    )
    
    chat_history = [
        {
            "role": "user",
            "parts": [{"text": f"{system_instruction}\n\nUser request: {prompt_text}"}]
        }
    ]
    
    payload = { "contents": chat_history }
    log_debug("Sending request to Gemini API...")
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        log_debug(f"Gemini API response status: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
        log_debug("Gemini API response received successfully.")
        
        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            
            manim_code = result["candidates"][0]["content"]["parts"][0]["text"]
            log_debug(f"Generated Manim code (truncated): {manim_code[:200]}...")
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
        log_debug(f"An unexpected error occurred during Gemini API call: {e}")
        raise

# --- Backend API Endpoint ---
@app.route('/generate-manim', methods=['POST'])
def generate_manim_animation():
    log_debug("Received request at /generate-manim")
    data = request.get_json()
    original_prompt = data.get('prompt')
    
    log_debug(f"Original prompt received: {original_prompt}")

    if not original_prompt:
        log_debug("Missing prompt in request body.")
        return jsonify({"message": "Prompt is required"}), 400

    current_prompt_for_ai = original_prompt
    manim_execution_failed_stderr = None

    for ai_code_attempt in range(MAX_AI_CODE_GENERATION_RETRIES):
        try:
            # 1. Call Gemini to get Manim Python code
            # If there was a previous Manim error, append it to the prompt for AI to fix
            if manim_execution_failed_stderr:
                log_debug(f"Attempting AI code regeneration (Attempt {ai_code_attempt + 1}/{MAX_AI_CODE_GENERATION_RETRIES}) with error feedback.")
                current_prompt_for_ai = (
                    f"{original_prompt}\n\n"
                    f"Previous Manim execution failed with the following error. "
                    f"Please review this error and provide corrected Manim code to resolve it:\n"
                    f"```\n{manim_execution_failed_stderr}\n```"
                )
            else:
                log_debug(f"Attempting initial AI code generation (Attempt {ai_code_attempt + 1}/{MAX_AI_CODE_GENERATION_RETRIES}).")
                current_prompt_for_ai = original_prompt # Reset for fresh attempts if previous was successful

            manim_code = get_manim_code_from_gemini(current_prompt_for_ai)
            
            # Clean up potential markdown code blocks from Gemini's response
            if manim_code.startswith("```python"):
                manim_code = manim_code.replace("```python", "").strip()
            if manim_code.endswith("```"):
                manim_code = manim_code.replace("```", "").strip()
            
            log_debug("Writing Manim code to file...")
            file_name = "main.py"
            file_path_absolute = os.path.join(OUTPUT_DIR_ABSOLUTE, file_name) 
            with open(file_path_absolute, "w") as f:
                f.write(manim_code)
            log_debug(f"Manim code saved to: {file_path_absolute}")

            # 2. Determine the scene name from the generated code
            scene_name = "CustomAnimation" # Default fallback
            for line in manim_code.splitlines():
                if "class" in line and "Scene" in line:
                    try:
                        scene_name = line.split("class")[1].split("(")[0].strip()
                        break
                    except IndexError:
                        log_debug("Failed to parse scene name. Using default.")

            log_debug(f"Using scene name: {scene_name}")

            # 3. Run Manim to generate and preview the video locally with retries
            manim_script_path_relative_to_root = os.path.join(OUTPUT_DIR_RELATIVE, file_name)

            manim_command = [
                "manim",
                "-pql", # -p for preview, -ql for low quality (faster)
                manim_script_path_relative_to_root, # Path to script relative to PROJECT_ROOT
                scene_name
            ]
            
            manim_execution_successful = False
            for manim_attempt in range(MAX_MANIM_EXECUTION_RETRIES):
                log_debug(f"Executing Manim command (AI Code Attempt {ai_code_attempt + 1}, Manim Execution Attempt {manim_attempt + 1}/{MAX_MANIM_EXECUTION_RETRIES}): {' '.join(manim_command)}")
                process = subprocess.run(manim_command, capture_output=True, text=True, cwd=PROJECT_ROOT)
                
                if process.returncode == 0:
                    log_debug("Manim command executed successfully. Video should open on server's display.")
                    manim_execution_successful = True
                    break # Break inner loop, Manim execution successful
                else:
                    log_debug(f"Manim command failed on Manim Execution Attempt {manim_attempt + 1}.\nStdout: {process.stdout}\nStderr: {process.stderr}")
                    manim_execution_failed_stderr = process.stderr # Capture stderr for AI feedback
                    if manim_attempt < MAX_MANIM_EXECUTION_RETRIES - 1:
                        log_debug(f"Retrying Manim execution in {RETRY_DELAY_SECONDS} seconds...")
                        time.sleep(RETRY_DELAY_SECONDS)
                    else:
                        log_debug(f"Manim command failed after {MAX_MANIM_EXECUTION_RETRIES} Manim execution attempts.")
                        # Do not raise exception yet, let outer loop handle regeneration
            
            if manim_execution_successful:
                return jsonify({"message": "Manim animation generated and opened on the server's display."})
            else:
                # If we are here, Manim execution failed after all retries.
                # The outer loop will now proceed to regenerate AI code with error feedback.
                continue # Continue to the next AI code generation attempt

        except requests.exceptions.RequestException as e:
            log_debug(f"HTTP error while calling Gemini API: {e}")
            return jsonify({"message": f"Failed to connect to AI service: {e}"}), 500
        except json.JSONDecodeError:
            log_debug(f"JSON decoding error: {response.text}")
            return jsonify({"message": "Invalid response from AI service."}), 500
        except Exception as e:
            log_debug(f"An unexpected error occurred during AI code generation or initial setup: {e}")
            # If an error occurs *before* Manim execution (e.g., Gemini API call fails),
            # we should not retry AI code generation based on Manim error.
            # Just return the error immediately.
            return jsonify({"message": str(e)}), 500

    # If we reach here, all AI code generation attempts failed
    final_error_message = f"Failed to generate and run Manim animation after {MAX_AI_CODE_GENERATION_RETRIES} AI code generation attempts."
    if manim_execution_failed_stderr:
        final_error_message += f" Last Manim error: {manim_execution_failed_stderr}"
    return jsonify({"message": final_error_message}), 500

if __name__ == '__main__':
    log_debug("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
