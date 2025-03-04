from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import json
from middleware.extractor import extract_main
from middleware.report_gen import analyze_with_model
import traceback

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
        raise HTTPException(status_code=500, detail="Error creating PDF directory")

    file_name = os.path.join(pdf_directory, file.filename)
    try:
        with open(file_name, 'wb') as f:
            contents = await file.read()
            f.write(contents)
    except Exception as e:
        print(f"Error writing file: {e}")
        raise HTTPException(status_code=500, detail="Error writing file")

    # Extracting text from PDF using custom OCR
    json_data = extract_main(file_name)

    if not json_data:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

    try:
        # Analyze the extracted text with the AI model
        model_output = await analyze_with_model(json_data)
        print(f"Model response: {model_output}")

        if isinstance(model_output, dict):
            return model_output
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from model")

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format")  # Specific error handling

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error during processing: {error_trace}")
        raise HTTPException(status_code=500, detail="Error processing PDF")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
