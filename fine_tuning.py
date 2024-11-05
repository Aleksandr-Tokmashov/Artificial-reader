import os
import subprocess
from pdf2image import convert_from_path

pdf_folder = 'pdf'
output_folder = 'output_images'
box_folder = os.path.join(output_folder, 'box_files')  # Папка для .box файлов

os.makedirs(output_folder, exist_ok=True)
os.makedirs(box_folder, exist_ok=True)

pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

pdf_files = pdf_files[:2]
print(pdf_files)

for filename in pdf_files:
    pdf_path = os.path.join(pdf_folder, filename)

    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Ошибка при преобразовании файла {pdf_path}: {e}")
        continue

    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'{filename[:-4]}_page_{i + 1}.png')
        image.save(image_path, 'PNG')

        box_filename = f'{filename[:-4]}_page_{i + 1}'
        box_file = os.path.join(box_folder, box_filename)  # Сохраняем в папку box_files
        result = subprocess.run(
            [r'C:\Program Files\Tesseract-OCR\tesseract.exe', image_path, box_file, '--psm', '6', 'batch.nochop', 'makebox'],
            capture_output=True
        )

        if result.returncode != 0:
            print(f"Ошибка Tesseract для {image_path}: {result.stderr.decode()}")


# Создаем lst файл
train_lst_path = os.path.join(output_folder, 'train.lst')
with open(train_lst_path, 'w') as lst_file:
    for box_filename in os.listdir(box_folder):
        if box_filename.endswith('.box'):
            img_filename = box_filename.replace('.box', '.png')
            img_path = os.path.abspath(os.path.join(output_folder, img_filename))
            box_path = os.path.abspath(os.path.join(box_folder, box_filename))

            if os.path.exists(img_path) and os.path.exists(box_path):
                lst_file.write(f"{img_path}\n{box_path}\n")
            else:
                print(f"Не найден файл: {img_path} или {box_path}")

training_command = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    train_lst_path,
    'output',
    '--psm',
    '6',
    'train',
    'lstm'
]


if not os.path.exists(train_lst_path):
    print(f"Не найден файл lst: {train_lst_path}")
else:
    result = subprocess.run(training_command, capture_output=True)

    if result.returncode == 0:
        print("Обучение завершено успешно.")
    else:
        print(f"Ошибка при обучении Tesseract: {result.stderr.decode()}")
