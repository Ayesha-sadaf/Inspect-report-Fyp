from fastapi import FastAPI ,File,UploadFile
import os
import sys
from middleware.pdf_to_image_converter import pdf_to_images
from middleware.extractor import extract_main
from middleware.csv_to_json import convert_csv_to_single_json
from middleware.report_gen import analyze_with_model
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
middleware_dir = os.path.join(current_dir, '..', '/middleware')  
sys.path.insert(0, middleware_dir)

app = FastAPI()

@app.get('/')
def root():
    return {"welcome to medical tool analyser..."}

@app.post("/upload-pdf")
async def create_upload_file(file: UploadFile= File(..., description="PDF file to upload", format="binary")):
    pdf_directory = "../pdf_files"
    try:
        if not os.path.exists(pdf_directory):
            os.makedirs(pdf_directory)
        print(f"PDF directory is located at: {os.path.abspath(pdf_directory)}")
    except Exception as e:
        print(f"Error creating PDF directory: {e}")

    file_name = os.path.join(pdf_directory, file.filename)
    try:
        with open(file_name,'wb') as f:
            contents= await file.read()
            f.write(contents)
    except:
        print(f"Error writing file: {e}")
    
  
    pdf_to_images(file_name,'./images.png')

    csv_data =extract_main('./images.png/report_img.png')

    json_data = convert_csv_to_single_json(csv_data)
    
    try:
        model_output = await analyze_with_model(json_data)
        return {
            "message": "PDF processed successfully",
            "model_analysis": model_output 
        }
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