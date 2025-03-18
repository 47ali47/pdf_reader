from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import re
import string



def process_text(text, num_letters=3):
    """Bold the first few letters of each word, excluding punctuation."""
    words = text.split()
    processed_words = []
    
    for word in words:
        # Handle leading punctuation
        leading_punct = ''
        while word and word[0] in string.punctuation:
            leading_punct += word[0]
            word = word[1:]
        
        # Handle trailing punctuation
        trailing_punct = ''
        while word and word[-1] in string.punctuation:
            trailing_punct = word[-1] + trailing_punct
            word = word[:-1]
        
        # If only punctuation or empty, add as is
        if not word:
            processed_words.append(leading_punct + trailing_punct)
            continue
        
        # Process the actual word
        if len(word) <= num_letters:
            processed_words.append(leading_punct + f"<b>{word}</b>" + trailing_punct)
        else:
            bold_part = word[:num_letters]
            rest = word[num_letters:]
            processed_words.append(leading_punct + f"<b>{bold_part}</b>{rest}" + trailing_punct)
    
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
    MAX_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    
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
        
        y = TOP_MARGIN
        
        for paragraph in processed_text.split('\n'):
            # Split paragraph into words and segments
            segments = []
            words = paragraph.split(' ')
            
            for word in words:
                word_segments = []
                parts = re.split(r'(<b>.*?</b>)', word)
                
                for part in parts:
                    if not part:
                        continue
                    if part.startswith('<b>') and part.endswith('</b>'):
                        word_segments.append((True, part[3:-4]))
                    else:
                        word_segments.append((False, part))
                segments.append(word_segments)
            
            # Process words into lines
            current_line = []
            current_width = 0
            
            for word_segments in segments:
                # Calculate total word width
                word_width = 0
                for is_bold, text in word_segments:
                    font = "Helvetica-Bold" if is_bold else "Helvetica"
                    word_width += c.stringWidth(text, font, FONT_SIZE)
                
                space_width = c.stringWidth(' ', "Helvetica", FONT_SIZE)
                
                # Check if adding this word would exceed line width
                if current_width + word_width + (space_width if current_line else 0) > MAX_WIDTH:
                    # Draw current line
                    x = LEFT_MARGIN
                    for i, word_parts in enumerate(current_line):
                        # Draw each segment of the word
                        for is_bold, text in word_parts:
                            c.setFont("Helvetica-Bold" if is_bold else "Helvetica", FONT_SIZE)
                            c.drawString(x, y, text)
                            x += c.stringWidth(text, "Helvetica-Bold" if is_bold else "Helvetica", FONT_SIZE)
                        # Add space after word (but not after the last word)
                        if i < len(current_line) - 1:
                            x += space_width
                    
                    # Move to next line
                    y -= LINE_HEIGHT
                    if y < BOTTOM_MARGIN:
                        c.showPage()
                        c.setFont("Helvetica", FONT_SIZE)
                        y = TOP_MARGIN
                    
                    # Start new line with current word
                    current_line = [word_segments]
                    current_width = word_width
                else:
                    # Add word to current line
                    current_line.append(word_segments)
                    current_width += word_width + (space_width if current_line else 0)
            
            # Draw remaining line if it exists
            if current_line:
                x = LEFT_MARGIN
                for i, word_parts in enumerate(current_line):
                    # Draw each segment of the word
                    for is_bold, text in word_parts:
                        c.setFont("Helvetica-Bold" if is_bold else "Helvetica", FONT_SIZE)
                        c.drawString(x, y, text)
                        x += c.stringWidth(text, "Helvetica-Bold" if is_bold else "Helvetica", FONT_SIZE)
                    # Add space after word (but not after the last word)
                    if i < len(current_line) - 1:
                        x += space_width
                y -= LINE_HEIGHT
            
            # Add extra space between paragraphs
            y -= LINE_HEIGHT/2
            
            # Check if we need a new page
            if y < BOTTOM_MARGIN:
                c.showPage()
                c.setFont("Helvetica", FONT_SIZE)
                y = TOP_MARGIN
        
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
