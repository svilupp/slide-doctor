import os
import subprocess
import fitz  # PyMuPDF

def convert_pptx_to_pdf(pptx_path, output_folder):
    # Check if LibreOffice is installed
    libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    if not os.path.exists(libreoffice_path):
        raise FileNotFoundError("LibreOffice is not installed in the default location.")

    # Prepare the output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert the .pptx to .pdf using LibreOffice
    command = [
        libreoffice_path,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_folder,
        pptx_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Converted {pptx_path} to PDF successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting the file: {e}")

def pdf_to_images(pdf_path, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load the page
        pix = page.get_pixmap()         # Render page to an image

        # Define output path for the image
        img_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(img_path)  # Save the image as PNG
        print(f"Saved: {img_path}")

    print(f"All pages saved as images in {output_folder}")

# Combined function to handle both conversions
def convert_pptx_to_images(pptx_file, output_folder):
    # Convert PPTX to PDF
    convert_pptx_to_pdf(pptx_file, output_folder)
    
    # Get the name of the converted PDF
    pdf_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pptx_file))[0] + '.pdf')
    
    # Convert PDF to images
    pdf_to_images(pdf_path, output_folder)

# Example usage
pptx_file = 'updated_presentation.pptx'  # Replace with your PPTX file path
output_folder = 'pics'  # Replace with your desired output folder

convert_pptx_to_images(pptx_file, output_folder)