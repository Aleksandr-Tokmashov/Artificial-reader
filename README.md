# Проектная работа "Искуственный чтец"
Этот проект предназначен для распознавания текста на изображениях с использованием различных моделей и инструментов. Основная цель — автоматизировать процесс анализа изображений и предоставить пользователю удобный интерфейс для работы с результатами.

## Содержание
- [Установка](#установка)
- [Базовый код](#базовый-код)
- [Структура проекта](#структура-проекта)
- [Стек](#стек)

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/ваш-репозиторий.git
    cd ваш-репозиторий
    ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

Основная модель, tesseract-ocr, должна быть установлен как системный пакет, не через pip

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

## Структура проекта
- **/Images** Папка с исходными изображениями
- /Modules                  # Модули проекта
- /Result                   # Папка с результатами распознавания
- /output_images            # Папка с выходными изображениями
- /pdf                      # Папка с PDF файлами
- /КО-инвест                # Папка с файлами для КО-инвест
- /HLIC                    # Папка с файлами для HLIC
- IOSUKE.png                # Пример изображения
- README.md                 # Документация проекта
- file_1.pdf                # Пример PDF файла
- requirements.txt          # Файл с зависимостями
- базовое_распознание_PNG.py # Скрипт базового распознавания PNG
- Продвинутое_распознание_PDF.py # Скрипт продвинутого распознавания PDF
- Продвинутое_распознание_PNG.py # Скрипт продвинутого распознавания PNG
- Разметка_1.py            # Скрипт разметки 1
- Разметка_2.py            # Скрипт разметки 2
- тестик.pdf                # Пример PDF файла

## Стек: 
* Python – основной язык программирования
* pytesseract – Python-обертка для Tesseract OCR для распознавания текста на изображениях
* pdf2image – библиотека для преобразования страниц PDF в изображения
* PIL/Pillow – библиотека для работы с изображениями
* Tesseract OCR – программа для оптического распознавания символов
* subprocess – модуль Python для выполнения внешних процессов
* os – модуль для работы с файловой системой


