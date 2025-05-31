import json
import random
import re
import streamlit as st # For error reporting in transform_output

def replace_german_sharp_s(text):
    """Replace all occurrences of 'ß' with 'ss'."""
    if isinstance(text, str):
        return text.replace('ß', 'ss')
    return text

def clean_json_string(s):
    """Cleans a string to make it valid JSON, focusing on common LLM output issues."""
    if not isinstance(s, str):
        return s # Or raise an error, or try to convert

    s = s.strip()
    # Remove markdown ```json ... ```
    s = re.sub(r'^```json\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*```$', '', s)
    s = s.strip()

    # Replace escaped newlines within string values properly
    # This regex looks for "key": "value with \n newlines"
    # and replaces \n with \\n ONLY within the quoted string values.
    # It's a bit tricky to get right for all cases.
    # A simpler approach for now:
    # s = s.replace('\n', '\\n') # This might be too broad, careful.

    # Attempt to ensure it's a list of objects or a single object
    # This is a common pattern for LLM JSON outputs.
    # If it's not starting with [ or {, try to find the first [ or {
    # This part is heuristic and might need refinement.
    first_char_index = -1
    for i, char in enumerate(s):
        if char in ['[', '{']:
            first_char_index = i
            break
    if first_char_index > 0:
        s = s[first_char_index:]

    # Remove trailing commas before closing ] or }
    s = re.sub(r',\s*(\}|\])', r'\1', s)
    
    # Remove non-printable characters (except newline if it's intended for structure)
    # s = ''.join(char for char in s if ord(char) >= 32 or char in ['\n', '\r', '\t'])

    # The original clean_json_string had more specific regexes, let's try to adapt them
    # s = re.sub(r'\s+', ' ', s) # This might break intended newlines in JSON strings
    # s = re.sub(r'(?<=text": ")(.+?)(?=")', lambda m: m.group(1).replace('\n', '\\n'), s) # This was good
    
    # A less aggressive cleaning for newlines within text values:
    # This is complex. For now, we rely on JSON parser to handle valid escapes.
    # The main issue is often unescaped newlines.
    # Let's assume the LLM is asked for JSON and it tries its best.
    # The ```json stripping is the most common fix needed.

    # Try to extract content between the first '[' and last ']' or first '{' and last '}'
    # This helps if there's extraneous text around the JSON array/object.
    json_match_array = re.search(r'(\[.*\])', s, re.DOTALL)
    json_match_object = re.search(r'(\{.*\})', s, re.DOTALL)

    if json_match_array:
        s = json_match_array.group(0)
    elif json_match_object: # If no array, try to find an object
        s = json_match_object.group(0)
    # If neither, the string might be malformed or not JSON.

    return s


def convert_json_to_text_format(json_input):
    """Converts JSON input (for inline_fib) to FIB and Inlinechoice text formats."""
    if isinstance(json_input, str):
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            # If direct loading fails, try with the cleaned string
            st.warning(f"JSONDecodeError in convert_json_to_text_format: {e}. Trying to clean.")
            cleaned_str = clean_json_string(json_input)
            try:
                data = json.loads(cleaned_str)
            except json.JSONDecodeError as e2:
                st.error(f"Still failed to parse JSON after cleaning: {e2}")
                st.text("Original problematic JSON string:")
                st.code(json_input, language='text')
                st.text("Cleaned problematic JSON string:")
                st.code(cleaned_str, language='text')
                raise ValueError("Invalid JSON for FIB/Inlinechoice conversion") from e2
    else:
        data = json_input # Assuming it's already a Python list/dict

    fib_output = []
    ic_output = []

    if not isinstance(data, list): # Ensure data is a list of items
        st.warning("FIB/Inlinechoice JSON data is not a list. Wrapping it in a list.")
        data = [data]


    for item in data:
        if not isinstance(item, dict):
            st.warning(f"Skipping non-dict item in FIB/Inlinechoice data: {item}")
            continue

        text = item.get('text', '')
        blanks = item.get('blanks', [])
        wrong_substitutes = item.get('wrong_substitutes', [])

        if not isinstance(blanks, list) or not isinstance(wrong_substitutes, list):
            st.error(f"Invalid 'blanks' or 'wrong_substitutes' in item: {item}. Skipping.")
            continue
            
        num_blanks = len(blanks)
        if num_blanks == 0 and "{blank}" not in text: # If no blanks are provided, and no placeholders in text
            st.warning(f"No blanks found for FIB/Inlinechoice item: {item}. Skipping this item.")
            continue


        # FIB Generation
        fib_lines = [
            "Type\tFIB",
            "Title\t✏✏Vervollständigen Sie die Lücken mit dem korrekten Begriff.✏✏",
            f"Points\t{num_blanks if num_blanks > 0 else 1}" # Ensure points is at least 1
        ]
        
        current_text_for_fib = text
        # Replace placeholders if blanks are provided
        if blanks:
            for blank_word in blanks:
                current_text_for_fib = current_text_for_fib.replace(blank_word, "{blank}", 1)
        
        parts = current_text_for_fib.split("{blank}")
        
        for index, part in enumerate(parts):
            fib_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks): # Ensure we have a blank for this part
                fib_lines.append(f"1\t{blanks[index]}\t20") # Points per blank, size
            elif index < num_blanks and not blanks: # Case where {blank} is in text but no blanks list
                 fib_lines.append(f"1\tCORRECT_ANSWER_UNDEFINED\t20")


        fib_output.append('\n'.join(fib_lines))

        # Inline Choice (IC) Generation
        ic_lines = [
            "Type\tInlinechoice",
            "Title\tWörter einordnen",
            "Question\t✏✏Wählen Sie die richtigen Wörter.✏✏",
            f"Points\t{num_blanks if num_blanks > 0 else 1}"
        ]

        all_options = blanks + wrong_substitutes
        random.shuffle(all_options)
        
        current_text_for_ic = text # Use original text for IC part splitting
        if blanks:
            for blank_word in blanks:
                current_text_for_ic = current_text_for_ic.replace(blank_word, "{blank}", 1)
        
        ic_parts = current_text_for_ic.split("{blank}")

        for index, part in enumerate(ic_parts):
            ic_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks): # Ensure we have a blank for this part
                options_str = '|'.join(all_options) if all_options else "OPTION_A|OPTION_B"
                correct_answer_for_ic = blanks[index]
                ic_lines.append(f"1\t{options_str}\t{correct_answer_for_ic}\t|")
            elif index < num_blanks and not blanks: # Case where {blank} is in text but no blanks list
                options_str = '|'.join(wrong_substitutes) if wrong_substitutes else "OPTION_A|OPTION_B"
                ic_lines.append(f"1\t{options_str}\tCORRECT_ANSWER_UNDEFINED\t|")


        ic_output.append('\n'.join(ic_lines))

    return '\n\n'.join(fib_output), '\n\n'.join(ic_output)


def transform_inline_fib_output(json_string):
    """Transforms JSON string for inline_fib questions into OLAT text format."""
    cleaned_json_string = clean_json_string(json_string)
    try:
        # Attempt to parse the cleaned JSON
        # The LLM is expected to return a list of objects for inline_fib
        # e.g., [{"text": "...", "blanks": ["..."], "wrong_substitutes": ["..."]}, ...]
        json_data = json.loads(cleaned_json_string)
        
        fib_output, ic_output = convert_json_to_text_format(json_data)
        
        fib_output = replace_german_sharp_s(fib_output)
        ic_output = replace_german_sharp_s(ic_output)

        return f"{ic_output}\n---\n{fib_output}"
    
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON for inline_fib: {e}")
        st.text("Cleaned JSON input that failed:")
        st.code(cleaned_json_string, language='json')
        st.text("Original JSON input:")
        st.code(json_string, language='text')
        
        # Attempt to salvage if it's a common issue like a missing closing bracket for a list
        # This is a very basic attempt and might not always work or be correct.
        salvaged = False
        if isinstance(cleaned_json_string, str) and cleaned_json_string.strip().startswith('[') and not cleaned_json_string.strip().endswith(']'):
            try:
                st.warning("Attempting to fix missing ']' in JSON array.")
                fixed_json_string = cleaned_json_string.strip() + ']'
                json_data = json.loads(fixed_json_string)
                fib_output, ic_output = convert_json_to_text_format(json_data)
                fib_output = replace_german_sharp_s(fib_output)
                ic_output = replace_german_sharp_s(ic_output)
                salvaged = True
                st.success("Successfully salvaged and processed partial JSON.")
                return f"{ic_output}\n---\n{fib_output}"
            except Exception as e_partial:
                st.error(f"Unable to salvage partial JSON: {e_partial}")
        
        if not salvaged:
            return "Error: Invalid JSON format for inline_fib processing."
            
    except ValueError as ve: # Catch ValueError from convert_json_to_text_format
        st.error(f"Error processing inline_fib data structure: {ve}")
        return "Error: Invalid data structure for inline_fib."

    except Exception as e:
        st.error(f"An unexpected error occurred during inline_fib transformation: {str(e)}")
        st.text("Original input:")
        st.code(json_string, language='text')
        return "Error: Unable to process inline_fib input."