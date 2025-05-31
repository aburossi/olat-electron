# In core/llm_service.py
def generate_via_llm(provider: str, api_key: str, model_name: str, system_prompt: str, user_prompt: str, images_base64_list: list = None, settings: dict = None):
    """
    Generic function to interact with an LLM provider.

    Args:
        provider (str): Name of the LLM provider (e.g., "openai").
        api_key (str): API key for the provider.
        model_name (str): Specific model to use.
        system_prompt (str): The system prompt.
        user_prompt (str): The user's prompt (potentially with placeholders resolved).
        images_base64_list (list, optional): List of base64 encoded images.
        settings (dict, optional): Additional provider-specific settings (e.g., temperature, response_format for OpenAI).

    Returns:
        str: The LLM's response (expected to be a JSON string or text).
    """
    if provider.lower() == "openai":
        from .providers import openai_provider # Use relative import
        try:
            return openai_provider.get_openai_response(
                api_key=api_key,
                model_name=model_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                images_base64_list=images_base64_list,
                settings=settings
            )
        except ConnectionError as e: # Catch specific error from provider
            # Log or handle as needed, then re-raise or return an error message
            # For now, re-raise to let the UI handle it.
            raise
        except Exception as e:
            # Catch any other unexpected errors from the provider
            raise ValueError(f"An unexpected error occurred with the OpenAI provider: {e}")

    # Example for future providers:
    # elif provider.lower() == "anthropic":
    #     from .providers import anthropic_provider # Create this module
    #     return anthropic_provider.get_anthropic_response(
    #         api_key=api_key,
    #         model_name=model_name,
    #         system_prompt=system_prompt,
    #         user_prompt=user_prompt,
    #         images_base64_list=images_base64_list,
    #         settings=settings
    #     )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")