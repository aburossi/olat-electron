import streamlit as st # For @st.cache_data
import os

@st.cache_data
def read_prompt_from_md(filename):
    """Read the prompt from a markdown file in the 'prompts' directory and cache the result."""
    # Construct path relative to this file or a known base directory if needed
    # For simplicity, assuming 'prompts' is in the current working directory or accessible path
    # A more robust solution would use os.path.join and __file__
    
    # Assuming the script is run from the root of olat-question-engine-v2
    prompt_file_path = os.path.join("prompts", f"{filename}.md")
    
    try:
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Prompt file not found: {prompt_file_path}")
        # Try looking in the current directory as a fallback (original behavior)
        try:
            with open(f"{filename}.md", "r", encoding="utf-8") as file:
                st.warning(f"Found prompt file {filename}.md in current directory instead of prompts/ folder.")
                return file.read()
        except FileNotFoundError:
            st.error(f"Prompt file {filename}.md also not found in current directory.")
            return None


def format_prompt(template_content, user_input, learning_goals):
    """
    Injects user input and learning goals into a prompt template.
    This is a basic example; more sophisticated templating might be needed.
    """
    # This is a placeholder. The actual formatting happens in generate_questions_ui
    # where MAIN INSTRUCTIONS, User Input, and Learning Goals are combined.
    # This function could be expanded if prompts have specific placeholders like {{user_input}}.
    # For now, the combination logic is:
    # f"MAIN INSTRUCTIONS:\n{template_content}\n\nUser Input: {user_input}\n\nLearning Goals: {learning_goals}"
    # This function could just return template_content if the above formatting is done by the caller.
    return template_content # Or implement more complex formatting if needed