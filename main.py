from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import re

def process_text(text, num_letters=2):
    """Bold the first few letters of each word."""
    words = text.split()
    processed_words = []
    
    for word in words:
        if len(word) <= num_letters:
            processed_words.append(f"<b>{word}</b>")
        else:
            bold_part = word[:num_letters]
            rest = word[num_letters:]
            processed_words.append(f"<b>{bold_part}</b>{rest}")
    
    return " ".join(processed_words)

def create_pdf_with_bold_text(input_path, output_path, num_letters=2):
    # Read the input PDF
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Process each page
    for page in reader.pages:
        # Extract text from the page
        text = page.extract_text()
        
        # Process the text to add bold formatting
        processed_text = process_text(text, num_letters)
        
        # Create a new PDF page with the processed text
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        
        # Set font
        c.setFont("Helvetica", 12)
        
        # Write the processed text
        y = 750  # Start from top of page
        for line in processed_text.split('\n'):
            # Handle bold text
            parts = re.split(r'(<b>.*?</b>)', line)
            x = 50  # Start from left margin
            
            for part in parts:
                if part.startswith('<b>') and part.endswith('</b>'):
                    # Bold text
                    text = part[3:-4]  # Remove tags
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(x, y, text)
                    x += c.stringWidth(text, "Helvetica-Bold", 12)
                elif part:
                    # Regular text
                    c.setFont("Helvetica", 12)
                    c.drawString(x, y, part)
                    x += c.stringWidth(part, "Helvetica", 12)
            
            y -= 15  # Move to next line
        
        c.save()
        
        # Get the value of the new PDF
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        # Add the new page to the output PDF
        writer.add_page(new_pdf.pages[0])
    
    # Save the output PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python main.py input.pdf output.pdf")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    
    try:
        create_pdf_with_bold_text(input_pdf, output_pdf)
        print(f"Successfully processed {input_pdf} and saved to {output_pdf}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
