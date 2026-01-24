"""AI service for code generation with error handling and self-correction."""
import logging
from pathlib import Path
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
# We'll configure inside the function to avoid fork safety issues with gRPC in Celery

# Maximum retry attempts for code generation
MAX_RETRY_ATTEMPTS = 3


class CodeGenerationError(Exception):
    """Raised when code generation fails."""
    pass


class SecurityViolationError(Exception):
    """Raised when generated code contains dangerous patterns."""
    pass


def _get_model(api_key: str = None):
    """Get configured Gemini model instance."""
    # Use provided key or fallback to settings (if any)
    key = api_key or settings.GEMINI_API_KEY
    if not key:
        raise CodeGenerationError("Gemini API Key is missing. Please provide one.")
        
    genai.configure(api_key=key)
    return genai.GenerativeModel(settings.MODEL_NAME)


def sanitize_code(code: str) -> str:
    """
    Check generated code for dangerous patterns.
    
    Raises:
        SecurityViolationError: If dangerous patterns are found.
    """
    code_lower = code.lower()
    
    for pattern in settings.dangerous_patterns:
        if pattern.lower() in code_lower:
            logger.warning(f"Security violation detected: {pattern}")
            raise SecurityViolationError(
                f"Generated code contains dangerous pattern: {pattern}. "
                "Code generation rejected for security reasons."
            )
    
    return code


def _clean_code_response(response_text: str) -> str:
    """Clean up AI response to extract pure Python code."""
    if not response_text:
        return ""
    
    # Remove markdown code blocks
    clean_code = response_text.replace("```python", "").replace("```", "").strip()
    
    # Remove any leading/trailing explanatory text
    lines = clean_code.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        # Start capturing at import or class/def
        if not in_code and (line.startswith('from ') or line.startswith('import ') or 
                           line.startswith('class ') or line.startswith('def ')):
            in_code = True
        
        if in_code:
            code_lines.append(line)
    
    return '\n'.join(code_lines) if code_lines else clean_code


def generate_code(prompt: str, api_key: str = None) -> str:
    """
    Generate Manim animation code using Gemini AI.
    
    Args:
        prompt: User's animation description
        api_key: Optional API key override
        
    Returns:
        Generated Python code
        
    Raises:
        CodeGenerationError: If generation fails
        SecurityViolationError: If code contains dangerous patterns
    """
    full_prompt = f"{settings.system_instruction}\n\nRequest: {prompt}"
    
    try:
        logger.info(f"Generating code for prompt: {prompt[:100]}...")
        
        model = _get_model(api_key)
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise CodeGenerationError("AI returned empty response")
        
        clean_code = _clean_code_response(response.text)
        
        # Security check
        sanitize_code(clean_code)
        
        logger.info("Code generation successful")
        return clean_code
        
    except SecurityViolationError:
        raise
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}", exc_info=True)
        raise CodeGenerationError(f"Failed to generate code: {str(e)}")


def fix_code(original_prompt: str, failed_code: str, error_message: str, attempt: int, api_key: str = None) -> str:
    """
    Ask AI to fix code that failed to render.
    
    Args:
        original_prompt: The original user request
        failed_code: The code that failed to execute
        error_message: The error message from Manim
        attempt: Current attempt number (1-indexed)
        api_key: Optional API key override
        
    Returns:
        Fixed Python code
        
    Raises:
        CodeGenerationError: If code fix fails
        SecurityViolationError: If fixed code contains dangerous patterns
    """
    
    fix_prompt = f"""{settings.system_instruction}

IMPORTANT: The previous code you generated failed with an error. You must fix it.

Original Request: {original_prompt}

Previous Code That Failed:
```python
{failed_code}
```

Error Message:
{error_message}

Fix Attempt: {attempt}/{MAX_RETRY_ATTEMPTS}

COMMON MANIM ERRORS AND FIXES:

1. TypeError: unsupported operand type(s) for -: 'method' and 'float'
   - CAUSE: Using .center instead of .get_center()
   - FIX: Replace obj.center with obj.get_center()
   - Also applies to: .top -> .get_top(), .bottom -> .get_bottom(), etc.

2. NameError: name 'PINK_D' is not defined
   - CAUSE: Invalid color name (PINK_D, ORANGE_D, etc. do not exist)
   - FIX: Use valid colors: PINK, ORANGE, RED, BLUE. Use hex codes for custom colors.

3. NameError: name 'ORANGE_D' is not defined
   - CAUSE: Invalid color name
   - FIX: Use ORANGE or hex code "#FFA500"

4. TypeError: shift() got unexpected keyword argument
   - CAUSE: Wrong method signature
   - FIX: Use .shift(direction * amount) not .shift(x=1, y=2)

5. ValueError: numpy array shape issues
   - CAUSE: 2D coordinates instead of 3D
   - FIX: Use np.array([x, y, 0]) for all positions

6. AttributeError: 'ManimConfig' object has no attribute 'frame_x_range'
   - CAUSE: Using non-existent config attributes like frame_x_range, frame_y_range, x_min, x_max
   - FIX: Do NOT use config properties. Use hardcoded values or config.frame_width.
   - Default frame width is approx 14.2, height is 8.0.

7. AttributeError: Axes object has no attribute 'add_labels'
   - CAUSE: .add_labels() does not exist in Manim Community.
   - FIX: Remove .add_labels(). Use .add_coordinates() to show numbers. To label axes names, use axes.get_axis_labels().

Instructions:
1. Analyze the error message carefully - the error type and line number are crucial
2. Find the EXACT line causing the error and fix it
3. Generate COMPLETE corrected code (not just the fix)
4. Double-check all .center, .top, .bottom, .left, .right - they should be .get_center(), .get_top(), etc.
5. Return ONLY the complete corrected Python code, no explanations

Generate the fixed code now:"""

    try:
        logger.info(f"Attempting to fix code (attempt {attempt}/{MAX_RETRY_ATTEMPTS})...")
        logger.info(f"Error being fixed: {error_message[:200]}...")
        
        model = _get_model(api_key)
        response = model.generate_content(fix_prompt)
        
        if not response.text:
            raise CodeGenerationError("AI returned empty response when fixing code")
        
        clean_code = _clean_code_response(response.text)
        
        # Security check
        sanitize_code(clean_code)
        
        logger.info(f"Code fix attempt {attempt} generated successfully")
        return clean_code
        
    except SecurityViolationError:
        raise
    except Exception as e:
        logger.error(f"Code fix failed: {str(e)}", exc_info=True)
        raise CodeGenerationError(f"Failed to fix code: {str(e)}")


def save_code(code: str, filename: Path = None) -> str:
    """
    Save generated code to file.
    
    Returns:
        Path to saved file
    """
    if filename is None:
        filename = settings.generated_animation_file
    
    try:
        # Ensure parent directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, "w") as f:
            f.write(code)
        logger.info(f"Code saved to {filename}")
        return str(filename)
    except IOError as e:
        logger.error(f"Failed to save code: {str(e)}")
        raise CodeGenerationError(f"Failed to save code: {str(e)}")
