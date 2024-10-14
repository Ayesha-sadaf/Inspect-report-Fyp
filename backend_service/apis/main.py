from fastapi import FastAPI, File, UploadFile
import os
import sys
import json  
from middleware.pdf_to_image_converter import pdf_to_images
from middleware.extractor import extract_main
from middleware.csv_to_json import convert_csv_to_single_json
from middleware.report_gen import analyze_with_model
import traceback


current_dir = os.path.dirname(os.path.abspath(__file__))
middleware_dir = os.path.join(current_dir, '..', 'middleware') 
sys.path.insert(0, middleware_dir)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"message": "Welcome to the medical tool analyzer..."}

@app.post("/upload-pdf")
async def create_upload_file(file: UploadFile = File(..., description="PDF file to upload", format="binary")):
    pdf_directory = "../pdf_files"
    try:
        if not os.path.exists(pdf_directory):
            os.makedirs(pdf_directory)
        print(f"PDF directory is located at: {os.path.abspath(pdf_directory)}")
    except Exception as e:
        print(f"Error creating PDF directory: {e}")

    file_name = os.path.join(pdf_directory, file.filename)
    try:
        with open(file_name, 'wb') as f:
            contents = await file.read()
            f.write(contents)
    except Exception as e:
        print(f"Error writing file: {e}")

    # Extracting images from the PDF
    pdf_to_images(file_name, './images.png')

    # Extracting CSV data
    csv_data = extract_main('./images.png/report_img.png')

    # Converting CSV data to JSON
    json_data = convert_csv_to_single_json(csv_data)

    try:
        model_output = await analyze_with_model(json_data)

 
        escaped_response = model_output.get("response", "")
        json_response = json.loads(escaped_response) 

        return json_response  
    except Exception as e:
    
        error_trace = traceback.format_exc() 
        print(f"Error during processing: {error_trace}") 

        return {
            "error": "Error processing PDF",
            "details": str(e), 
            "traceback": error_trace 
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
