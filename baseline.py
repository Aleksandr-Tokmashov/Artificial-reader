import pytesseract
from pdf2image import convert_from_path
from PIL import Image


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

def recognize_text(image):
    custom_config = r'--oem 1 --psm 6 -l rus'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

pdf_path = "file_1.pdf"
images = pdf_to_images(pdf_path)

for i, image in enumerate(images):
    text = recognize_text(image)
    print(f"Распознанный текст на странице {i + 1}:", text)
