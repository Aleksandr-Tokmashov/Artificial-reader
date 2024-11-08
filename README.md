# Проектная работа "Искуственный чтец"

Стек: 
* Python – основной язык программирования
* pytesseract – Python-обертка для Tesseract OCR для распознавания текста на изображениях
* pdf2image – библиотека для преобразования страниц PDF в изображения
* PIL/Pillow – библиотека для работы с изображениями
* Tesseract OCR – программа для оптического распознавания символов
* subprocess – модуль Python для выполнения внешних процессов
* os – модуль для работы с файловой системой

Структура проекта:
- pdf/ — папка с PDF файлами
- output_images/ — папка с PDF файлами
- Images/ — изображения для чтения
- Modules/ — папка с модулями проекта
- Result/ — папка с файлами, полученными после отработки основной программы

**Важные файлы:**
//Добавить потом если не лень//

## Установка и запуск
Все нужные библиотеки находятся в файле `requirements.txt`

Основная модель, tesseract-ocr, должна быть установлен как системный пакет, не через pip

//Добавить ссылку на скачивание//

### Базовый код

```python
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

```
