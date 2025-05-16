import pytesseract
from PIL import Image
import io
from app.config import settings

def process_image(image_bytes: bytes) -> str:
    """
    Process an image and extract text using OCR
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale for better OCR results
        image = image.convert('L')
        
        # Apply OCR
        text = pytesseract.image_to_string(image)
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def process_multiple_images(images: list) -> str:
    """
    Process multiple images and combine the text
    """
    all_text = []
    for image in images:
        text = process_image(image)
        all_text.append(text)
    
    return "\n".join(all_text)
