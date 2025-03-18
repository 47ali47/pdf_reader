from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import re
import textwrap

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
    
    # Define page dimensions and margins
    PAGE_WIDTH, PAGE_HEIGHT = letter
    LEFT_MARGIN = 50
    RIGHT_MARGIN = 50
    TOP_MARGIN = 750
    BOTTOM_MARGIN = 50
    LINE_HEIGHT = 15
    FONT_SIZE = 12
    
    # Calculate maximum line width
    TEXT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    
    # Process each page
    for page in reader.pages:
        # Extract text from the page
        text = page.extract_text()
        
        # Process the text to add bold formatting
        processed_text = process_text(text, num_letters)
        
        # Create a new PDF page with the processed text
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", FONT_SIZE)
        
        # Split text into lines that fit within margins
        y = TOP_MARGIN
        current_line = []
        current_line_width = 0
        
        # Process each line
        for line in processed_text.split('\n'):
            # Split line into segments while preserving bold tags
            segments = []
            parts = re.split(r'(<b>.*?</b>)', line)
            
            for part in parts:
                if not part:
                    continue
                    
                if part.startswith('<b>') and part.endswith('</b>'):
                    # Bold text segment
                    text = part[3:-4]
                    segments.append(('bold', text))
                else:
                    # Regular text - split into words
                    words = part.split()
                    for word in words:
                        segments.append(('regular', word))
            
            # Process segments into lines
            for i, (style, text) in enumerate(segments):
                # Calculate word width
                font = "Helvetica-Bold" if style == 'bold' else "Helvetica"
                word_width = c.stringWidth(text, font, FONT_SIZE)
                space_width = c.stringWidth(' ', "Helvetica", FONT_SIZE)
                
                # Check if we need to start a new line
                if current_line and (current_line_width + word_width + space_width > TEXT_WIDTH):
                    # Draw current line
                    x = LEFT_MARGIN
                    for j, (line_style, line_text) in enumerate(current_line):
                        # Set appropriate font
                        c.setFont("Helvetica-Bold" if line_style == 'bold' else "Helvetica", FONT_SIZE)
                        # Draw the word
                        c.drawString(x, y, line_text)
                        # Move x position, adding space if not last word
                        x += c.stringWidth(line_text, "Helvetica-Bold" if line_style == 'bold' else "Helvetica", FONT_SIZE)
                        if j < len(current_line) - 1:  # Add space only between words
                            x += space_width
                            
                    # Move to next line
                    y -= LINE_HEIGHT
                    if y < BOTTOM_MARGIN:
                        c.showPage()
                        c.setFont("Helvetica", FONT_SIZE)
                        y = TOP_MARGIN
                    
                    # Start new line with current word
                    current_line = [(style, text)]
                    current_line_width = word_width
                else:
                    # Add word to current line
                    current_line.append((style, text))
                    current_line_width += word_width + (space_width if current_line else 0)
            
            # Draw remaining line if it exists
            if current_line:
                x = LEFT_MARGIN
                for j, (line_style, line_text) in enumerate(current_line):
                    c.setFont("Helvetica-Bold" if line_style == 'bold' else "Helvetica", FONT_SIZE)
                    c.drawString(x, y, line_text)
                    x += c.stringWidth(line_text, "Helvetica-Bold" if line_style == 'bold' else "Helvetica", FONT_SIZE)
                    if j < len(current_line) - 1:  # Add space only between words
                        x += space_width
                
                # Move to next line
                y -= LINE_HEIGHT
                if y < BOTTOM_MARGIN:
                    c.showPage()
                    c.setFont("Helvetica", FONT_SIZE)
                    y = TOP_MARGIN
                current_line = []
                current_line_width = 0
        
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
