"""AI service for code generation with error handling."""
import logging
from pathlib import Path
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.MODEL_NAME)


class CodeGenerationError(Exception):
    """Raised when code generation fails."""
    pass


class SecurityViolationError(Exception):
    """Raised when generated code contains dangerous patterns."""
    pass


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


def generate_code(prompt: str) -> str:
    """
    Generate Manim animation code using Gemini AI.
    
    Args:
        prompt: User's animation description
        
    Returns:
        Generated Python code
        
    Raises:
        CodeGenerationError: If generation fails
        SecurityViolationError: If code contains dangerous patterns
    """
    if not settings.GEMINI_API_KEY:
        raise CodeGenerationError("GEMINI_API_KEY not configured")
    
    full_prompt = f"{settings.system_instruction}\n\nRequest: {prompt}"
    
    try:
        logger.info(f"Generating code for prompt: {prompt[:100]}...")
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise CodeGenerationError("AI returned empty response")
        
        # Clean up markdown code blocks if present
        clean_code = response.text.replace("```python", "").replace("```", "").strip()
        
        # Security check
        sanitize_code(clean_code)
        
        logger.info("Code generation successful")
        return clean_code
        
    except SecurityViolationError:
        raise
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}", exc_info=True)
        raise CodeGenerationError(f"Failed to generate code: {str(e)}")


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
