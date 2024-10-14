import fitz  # PyMuPDF
from PIL import Image
import os

def pdf_to_images(pdf_path, output_folder):
    """Convert a PDF file to images and save them in the specified folder."""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)
        
        # Render the page to a pixmap (image)
        pix = page.get_pixmap()
        
        # Convert pixmap to a PIL image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save the image
        img_name = "report_img"
        print("imag name is",img_name)
        image_file = os.path.join(output_folder, f'{img_name}.png')
        img.save(image_file, 'PNG')
        print(f'Saved: {output_folder}')
