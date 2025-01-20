import streamlit as st
import os
import time
from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2, LLMWhispererClientException

def extract_text_with_llmwhisperer(file_path, api_key, sync_mode=True, wait_timeout=200):
    """
    Extract text from a file using the LLMWhisperer API.
    """
    # Initialize the client
    client = LLMWhispererClientV2(api_key=api_key)

    try:
        if sync_mode:
            # Synchronous processing
            result = client.whisper(
                file_path=file_path,
                wait_for_completion=True,
                wait_timeout=wait_timeout,
            )
            return result.get("extraction", {}).get("result_text", "No text extracted.")
        else:
            # Asynchronous processing
            result = client.whisper(file_path=file_path)
            whisper_hash = result.get("whisper_hash")
            if not whisper_hash:
                return "Failed to retrieve whisper hash."

            while True:
                status = client.whisper_status(whisper_hash=whisper_hash)
                if status["status"] == "processing":
                    st.info("Processing...")
                elif status["status"] == "processed":
                    result = client.whisper_retrieve(whisper_hash=whisper_hash)
                    return result.get("extraction", {}).get("result_text", "No text extracted.")
                elif status["status"] in ("unknown", "failed"):
                    return f"Error: {status['status']}."
                time.sleep(5)  # Poll every 5 seconds
    except LLMWhispererClientException as e:
        return f"Error: {e.message}, Status Code: {e.status_code}"


# Streamlit App
st.title("LLMWhisperer Text Extraction")
st.write("Upload a document and provide your API key to extract text.")

# File Upload
uploaded_file = st.file_uploader("Upload your file", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
api_key = st.text_input("API Key", type="password")

# Extract Button
if st.button("Extract Text"):
    if not uploaded_file:
        st.error("Please upload a file.")
    elif not api_key:
        st.error("Please provide an API key.")
    else:
        # Save the uploaded file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)

        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Extract text
            st.info("Extracting text...")
            extracted_text = extract_text_with_llmwhisperer(file_path, api_key, sync_mode=True)

            if extracted_text:
                st.success("Text Extraction Successful!")
                st.text_area("Extracted Text", value=extracted_text, height=300)
            else:
                st.error("Failed to extract text.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
