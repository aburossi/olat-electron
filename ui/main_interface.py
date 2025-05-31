import streamlit as st
from PIL import Image
import logging

from core import config
from core.file_processor import (
    extract_text_from_docx, 
    process_uploaded_pdf,
    process_image_for_api
)
from core.prompt_builder import read_prompt_from_md
from core.output_formatter import transform_inline_fib_output, replace_german_sharp_s
from core.llm_service import generate_via_llm
from .info_sections import display_all_info_sections, apply_custom_css


def generate_questions_ui(user_input, learning_goals, selected_types, image_pil_object, selected_language, openai_api_key):
    """
    Handles the UI logic for generating questions and displaying results.
    'image_pil_object' should be a PIL Image object or None.
    """
    all_responses = ""
    generated_content_summary = {} # To display summary like "✔ Single Choice"

    # Prepare image if present
    base64_image_str = None
    if image_pil_object:
        try:
            base64_image_str = process_image_for_api(image_pil_object)
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return # Stop generation if image processing fails

    images_base64_list = [base64_image_str] if base64_image_str else None

    with st.spinner("Generating questions... This may take a moment."):
        for msg_type in selected_types:
            st.write(f"Generating for type: {msg_type}...")
            prompt_template_content = read_prompt_from_md(msg_type)
            if not prompt_template_content:
                st.error(f"Could not load prompt template for {msg_type}. Skipping.")
                continue

            # The user_prompt for the LLM includes the template, user's text, and learning goals
            full_user_prompt = (
                f"MAIN INSTRUCTIONS:\n{prompt_template_content}\n\n"
                f"User Input: {user_input}\n\n"
                f"Learning Goals: {learning_goals}\n\n"
                f"Output Language: {selected_language}" # Explicitly pass selected language
            )
            
            llm_settings = {
                "temperature": config.DEFAULT_TEMPERATURE,
                "max_tokens": config.DEFAULT_MAX_TOKENS,
            }
            # If the prompt type is expected to be JSON (e.g. inline_fib), set response_format
            if msg_type == "inline_fib":
                 llm_settings["response_format"] = {"type": "json_object"}


            try:
                response = generate_via_llm(
                    provider="openai",
                    api_key=openai_api_key,
                    model_name=config.DEFAULT_MODEL_NAME,
                    system_prompt=config.SYSTEM_PROMPT_EDUCATOR, # Using the global system prompt
                    user_prompt=full_user_prompt,
                    images_base64_list=images_base64_list,
                    settings=llm_settings
                )

                if response:
                    processed_response = ""
                    if msg_type == "inline_fib":
                        # transform_inline_fib_output handles JSON parsing and formatting
                        processed_response = transform_inline_fib_output(response)
                        # The raw JSON response might also be useful for debugging
                        # st.text(f"Raw JSON response for {msg_type}:")
                        # st.code(response, language='json')
                    else:
                        # For other types, apply general cleaning
                        processed_response = replace_german_sharp_s(response)
                    
                    generated_content_summary[f"{msg_type.replace('_', ' ').title()}"] = True # Mark as successful
                    all_responses += f"--- {msg_type.upper()} ---\n{processed_response}\n\n"
                else:
                    st.error(f"Failed to generate a response for {msg_type}.")
                    generated_content_summary[f"{msg_type.replace('_', ' ').title()}"] = False # Mark as failed
            
            except ConnectionError as e: # Specific error from llm_service for provider issues
                st.error(f"API Error for {msg_type}: {e}")
                generated_content_summary[f"{msg_type.replace('_', ' ').title()}"] = False
            except ValueError as e: # For unsupported provider or other llm_service errors
                st.error(f"Configuration Error for {msg_type}: {e}")
                generated_content_summary[f"{msg_type.replace('_', ' ').title()}"] = False
            except Exception as e:
                st.error(f"An unexpected error occurred while generating for {msg_type}: {str(e)}")
                logging.exception(f"Error during question generation for {msg_type}")
                generated_content_summary[f"{msg_type.replace('_', ' ').title()}"] = False
    
    st.subheader("Generation Summary:")
    for title, success in generated_content_summary.items():
        st.write(f"{'✔' if success else '❌'} {title}")

    if all_responses:
        st.download_button(
            label="Download All Generated Content",
            data=all_responses.strip(), # Remove trailing newlines
            file_name="all_generated_responses.txt",
            mime="text/plain"
        )

def run_app():
    st.set_page_config(page_title="OLAT Fragen Generator - Version Lehrmittel", page_icon="📝", layout="centered")
    st.title("OLAT Fragen Generator - Version Lehrmittel")

    # Apply custom CSS for info boxes
    apply_custom_css()

    # API Key Check
    try:
        openai_api_key = st.secrets["openai"]["api_key"]
    except (KeyError, FileNotFoundError): # FileNotFoundError for local dev if secrets file is missing
        st.error("OpenAI API key not found in Streamlit Secrets. Please add it to continue.")
        st.markdown("Refer to Streamlit documentation for managing secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management")
        return # Stop the app if API key is not found

    # Settings Section
    st.subheader("Einstellungen")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Sprache auswählen:")
        languages = {"German": "German", "English": "English", "French": "French", "Italian": "Italian", "Spanish": "Spanish"}
        selected_language = st.radio("Wählen Sie die Sprache für den Output:", list(languages.values()), index=0)
    with col2:
        display_all_info_sections()

    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF, DOCX, or image file", type=["pdf", "docx", "jpg", "jpeg", "png"])

    text_content_from_file = ""
    # image_content_from_file is a PIL Image object if an image is uploaded or PDF page is converted
    image_content_from_file = None 
    # images_from_pdf is a list of PIL Image objects if PDF is multi-page and non-OCR
    images_from_pdf = [] 

    # Clear cache if a new file is uploaded (Streamlit handles this for widgets,
    # but explicit clear for @st.cache_data might be needed if inputs to cached funcs change based on file)
    # For now, relying on Streamlit's default behavior. If issues arise, add:
    # if uploaded_file and "last_uploaded_filename" not in st.session_state or \
    #    st.session_state.last_uploaded_filename != uploaded_file.name:
    #    st.cache_data.clear()
    #    st.session_state.last_uploaded_filename = uploaded_file.name


    if uploaded_file:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            # process_uploaded_pdf returns (text, images_list)
            text_content_from_file, images_from_pdf = process_uploaded_pdf(uploaded_file)
            if text_content_from_file:
                st.success("Text aus PDF extrahiert. Sie können es nun im folgenden Textfeld bearbeiten. PDFs, die länger als 5 Seiten sind, sollten gekürzt werden.")
            elif images_from_pdf:
                st.success(f"{len(images_from_pdf)} PDF Seite(n) zu Bildern konvertiert. Sie können nun Fragen zu jeder Seite stellen.")
            else:
                st.error("Konnte PDF weder als Text noch als Bilder verarbeiten.")
        
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text_content_from_file = extract_text_from_docx(uploaded_file)
            st.success("Text aus DOCX erfolgreich extrahiert. Sie können ihn im Textbereich unten bearbeiten.")
        
        elif file_type.startswith('image/'):
            image_content_from_file = Image.open(uploaded_file)
            st.image(image_content_from_file, caption='Hochgeladenes Bild', use_column_width=True)
            st.success("Bild erfolgreich hochgeladen. Sie können nun Fragen zum Bild stellen.")
        else:
            st.error("Nicht unterstützter Dateityp. Bitte laden Sie eine PDF-, DOCX- oder Bilddatei hoch.")

    # Main interaction area
    if images_from_pdf: # Multi-page PDF processing
        for idx, page_image_pil in enumerate(images_from_pdf):
            st.markdown(f"--- Seite {idx + 1} ---")
            st.image(page_image_pil, caption=f'Seite {idx+1}', use_column_width=True)
            
            user_input_page = st.text_area(f"Ihre Frage oder Anweisungen für Seite {idx+1}:", key=f"text_area_page_{idx}")
            learning_goals_page = st.text_area(f"Lernziele für Seite {idx+1} (Optional):", key=f"learning_goals_page_{idx}")
            selected_types_page = st.multiselect(f"Fragetypen für Seite {idx+1} auswählen:", config.MESSAGE_TYPES, key=f"selected_types_page_{idx}")

            if st.button(f"Fragen für Seite {idx+1} generieren", key=f"generate_button_page_{idx}"):
                if (user_input_page or page_image_pil) and selected_types_page:
                    with st.container(): # Group output for this page
                         generate_questions_ui(user_input_page, learning_goals_page, selected_types_page, page_image_pil, selected_language, openai_api_key)
                elif not selected_types_page:
                    st.warning(f"Bitte wählen Sie mindestens einen Fragetyp für Seite {idx+1} aus.")
                else: # No user input and no image (though page_image_pil should always be there)
                    st.warning(f"Bitte geben Sie Text ein oder stellen Sie sicher, dass das Bild für Seite {idx+1} verarbeitet wurde.")
    
    else: # Single text input or single image processing
        user_input_main = st.text_area("Geben Sie hier Ihren Text ein oder stellen Sie eine Frage zum Bild:", value=text_content_from_file if text_content_from_file else "")
        learning_goals_main = st.text_area("Lernziele (Optional):")
        selected_types_main = st.multiselect("Wählen Sie die zu generierenden Fragetypen aus:", config.MESSAGE_TYPES)

        if st.button("Fragen generieren"):
            if (user_input_main or image_content_from_file) and selected_types_main:
                generate_questions_ui(user_input_main, learning_goals_main, selected_types_main, image_content_from_file, selected_language, openai_api_key)
            elif not user_input_main and not image_content_from_file:
                st.warning("Bitte geben Sie Text ein, laden Sie eine Datei hoch oder laden Sie ein Bild hoch.")
            elif not selected_types_main:
                st.warning("Bitte wählen Sie mindestens einen Fragetyp aus.")