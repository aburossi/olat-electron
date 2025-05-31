from openai import OpenAI
import httpx
import logging

# Local import from the same package (core)
from ..file_processor import process_image_for_api # Adjusted import

# Initialize a custom httpx client without proxies
# This relies on proxy env vars being cleared by core.config
http_client = httpx.Client()

def get_openai_response(api_key: str, model_name: str, system_prompt: str, user_prompt: str, images_base64_list: list = None, settings: dict = None):
    """
    Fetches response from OpenAI GPT.

    Args:
        api_key (str): API key for OpenAI.
        model_name (str): Specific OpenAI model to use.
        system_prompt (str): The system prompt.
        user_prompt (str): The user's prompt.
        images_base64_list (list, optional): List of base64 encoded image strings.
        settings (dict, optional): Additional OpenAI-specific settings 
                                   (e.g., temperature, max_tokens, response_format).

    Returns:
        str: The LLM's response content.
    """
    try:
        client = OpenAI(
            api_key=api_key,
            http_client=http_client # Use the pre-configured client
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        user_content = [{"type": "text", "text": user_prompt}]
        if images_base64_list:
            for base64_image_str in images_base64_list:
                # The process_image_for_api function is now expected to return a base64 string.
                # If it's already base64, it can just pass it through or ensure correct format.
                # For this provider, we assume images_base64_list contains ready-to-use base64 strings.
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image_str}",
                        "detail": "low" # As per original app
                    }
                })
        
        messages.append({"role": "user", "content": user_content})

        # Default settings if not provided
        api_settings = {
            "temperature": 0.4, # from original app
            "max_tokens": 16000, # from original app
            # "response_format": {"type": "json_object"}, # Enable if all responses should be JSON
            **(settings or {}) # Merge/override with provided settings
        }
        
        # If a specific response_format is requested (like json_object), ensure it's passed
        # For example, settings could be {"response_format": {"type": "json_object"}}

        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            **api_settings
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error communicating with OpenAI API: {e}")
        # Re-raise the exception so the caller (llm_service) can handle it or propagate it
        raise ConnectionError(f"OpenAI API request failed: {e}") from e