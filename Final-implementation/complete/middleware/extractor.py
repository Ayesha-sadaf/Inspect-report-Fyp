import requests
import json
import os
from dotenv import load_dotenv

def extract_text_from_pdf(pdf_path):
    """Send PDF to custom OCR endpoint and get the extracted text."""
    url = "http://173.249.36.80:10000/process_pdf/"

    try:
        # Open the PDF file and send it as multipart/form-data
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': pdf_file}
            response = requests.post(url, files=files)

        print(f"OCR API Response Status: {response.status_code}")
        print(f"OCR API Response Body: {response.text}")

        if response.status_code != 200:
            print(f"Error: OCR API returned status code {response.status_code}")
            return None

        # Parse the OCR response
        ocr_result = response.json()
        extracted_text = ""
        for page in ocr_result.get('results', []):
            extracted_text += f"Page {page['page_number']}:\n{page['text']}\n"
        return extracted_text

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return None

def extract_main(file_name):
    """Main function to extract text and generate output for model."""
    
    extracted_text = extract_text_from_pdf(file_name)
    if not extracted_text:
        print("Failed to extract text from PDF")
        return None

    # Prepare the data for the AI model
    json_data = {
        "text": extracted_text
    }
    
    return json_data
