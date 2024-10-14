import fitz  # PyMuPDF
from PIL import Image
import os

def pdf_to_images(pdf_path, output_folder):
    """Convert a PDF file to images and save them in the specified folder."""
    os.makedirs(output_folder, exist_ok=True)
    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_name = "report_img"
        print("imag name is",img_name)
        image_file = os.path.join(output_folder, f'{img_name}.png')
        img.save(image_file, 'PNG')
        print(f'Saved: {output_folder}')
