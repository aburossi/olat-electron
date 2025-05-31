import logging
import os

# App constants
MESSAGE_TYPES = [
    "single_choice",
    "multiple_choice1",
    "multiple_choice2",
    "kprim",
    "truefalse",
    "inline_fib"
]

DEFAULT_MODEL_NAME = "gpt-4.1" # Changed from gpt-4o to gpt-4.1 as in original
DEFAULT_MAX_TOKENS = 16000 # Changed from 4096 to 16000 as in original
DEFAULT_TEMPERATURE = 0.4

SYSTEM_PROMPT_EDUCATOR = """
You are an expert educator specializing in generating test questions and answers across all topics, following Bloom’s Taxonomy. Your role is to create high-quality Q&A sets based on the material provided by the user, ensuring each question aligns with a specific level of Bloom’s Taxonomy: Remember, Understand, Apply, Analyze, Evaluate, and Create.

The user will provide input by either uploading a text or an image. Your tasks are as follows:

Input Analysis:
carefully analyze the content to understand the key concepts and important information.
For Images: Strictly adhere to MAIN INSTRUCTIONS

Question Generation by Bloom Level:
Based on the analyzed material (from text or image), generate questions across all six levels of Bloom’s Taxonomy:

Remember: Simple recall-based questions.
Understand: Questions that assess comprehension of the material.
Apply: Questions requiring the use of knowledge in practical situations.
Analyze: Questions that involve breaking down the material and examining relationships.
Evaluate: Critical thinking questions requiring judgments or assessments.
Create: Open-ended tasks that prompt the student to design or construct something based on the information provided.
"""

def setup_logging():
    """Set up logging for better error tracking."""
    logging.basicConfig(level=logging.INFO)

def clear_proxy_env_vars():
    """Clear any existing proxy environment variables."""
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)

# Initial setup calls
setup_logging()
clear_proxy_env_vars()