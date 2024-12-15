import spacy
from spacy.tokens import DocBin
import re
import json
import pandas as pd
from pdfplumber import open as pdf_open
from docx import Document
import os

# Директории с файлами
pdf_directory = "КО-инвест"
word_directory = "НЦС"

# Метки и шаблоны
labels = {
    "TYPE": r"(ru[A-Za-z0-9.-]+|Тип|Наименование|Этажность|Объект)",
    "UNIT": r"(м²|шт|км|РУБ|м³|на 1 м2)",
    "COST": r"(\d+\s?[RР]уб\.|\d+[.,]?\d*\s?[РРУБ]+|\d+\s?Econom|\d+\s?[xX]{2}\d{2}\s?РУБ)",
    "CODE": r"(А\d+\.\d+\.\d+\.\d+|\d{2,}-\d{2,})",
    "SCHEME": r"(каркасный|деревянный|бетонный|глиносоломенный|кровля|полы)"
}

# 1. Извлечение текста
def extract_text_from_pdf(pdf_path):
    with pdf_open(pdf_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages])

def extract_text_from_word(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(directory, file_type):
    texts = []
    for file_name in os.listdir(directory):
        if file_name.endswith(file_type):
            file_path = os.path.join(directory, file_name)
            if file_type == ".pdf":
                texts.append({"text": extract_text_from_pdf(file_path), "source": file_name})
            elif file_type == ".docx":
                texts.append({"text": extract_text_from_word(file_path), "source": file_name})
    return texts

pdf_texts = extract_text(pdf_directory, ".pdf")
word_texts = extract_text(word_directory, ".docx")
all_texts = pdf_texts + word_texts

# 2. Очистка текста
def clean_text(text):
    cleaned_text = re.sub(r'[^\w\s,.()\-:;]', '', text)
    return cleaned_text

# 3. Автоматическая разметка текста
def auto_annotate(text, patterns):
    entities = []
    for label, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            start, end = match.start(), match.end()
            entities.append((start, end, label))
    return {"text": text, "entities": entities}

annotated_data = [auto_annotate(entry["text"], labels) for entry in all_texts]

# Фильтрация пересекающихся сущностей
def filter_overlapping_entities(entities):
    """Удаляем пересекающиеся сущности."""
    filtered_entities = []
    sorted_entities = sorted(entities, key=lambda x: x[0])
    last_end = -1
    for start, end, label in sorted_entities:
        if start >= last_end:
            filtered_entities.append((start, end, label))
            last_end = end
    return filtered_entities

for entry in annotated_data:
    entry["entities"] = filter_overlapping_entities(entry["entities"])

# 4. Конвертация данных в формат spaCy
def convert_to_spacy_format(data, output_file):
    nlp = spacy.blank("ru")
    db = DocBin()
    for entry in data:
        cleaned_text = clean_text(entry["text"])
        doc = nlp(cleaned_text)
        ents = []
        for start, end, label in entry["entities"]:
            span = doc.char_span(start, end, label=label)
            if span:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk(output_file)

# 5. Разделение данных и создание spacy-файлов
train_data = annotated_data[:int(len(annotated_data) * 0.8)]
test_data = annotated_data[int(len(annotated_data) * 0.8):]

convert_to_spacy_format(train_data, "train.spacy")
convert_to_spacy_format(test_data, "test.spacy")

def check_spacy_file(file_path):
    db = DocBin().from_disk(file_path)
    docs = list(db.get_docs(spacy.blank("ru").vocab))
    print(f"Проверено {len(docs)} документов в файле {file_path}.")
    for doc in docs:
        print(doc.text)
        for ent in doc.ents:
            print(f"  Сущность: {ent.text}, Метка: {ent.label_}")

check_spacy_file("train.spacy")
check_spacy_file("test.spacy")


# 6. Обучение модели
def train_model():
    config = """
[paths]
train = "./train.spacy"
dev = "./test.spacy"

[system]
seed = 42

[nlp]
lang = "ru"
pipeline = ["ner"]
batch_size = 128
tokenizer = {"@tokenizers": "spacy.Tokenizer.v1"}
before_creation = null
after_creation = null
after_pipeline_creation = null

[components]
[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true

[components.ner.model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v2"
width = 96
depth = 4
embed_size = 2000

[corpora]
[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}

[training]
seed = 42
dropout = 0.2
max_epochs = 10

[initialize]
vectors = null
init_tok2vec = null

[initialize.components]
[initialize.components.ner]
labels = ["TYPE", "UNIT", "COST", "CODE", "SCHEME"]
"""
    with open("config_filled.cfg", "w", encoding="utf-8") as f:
        f.write(config)

    os.system("python -m spacy train config_filled_filled.cfg --output ./output --paths.train ./train.spacy --paths.dev ./test.spacy")

train_model()

# 7. Применение модели
def apply_model(texts, model_path):
    nlp = spacy.load(model_path)
    results = []
    for entry in texts:
        doc = nlp(entry["text"])
        results.append({"source": entry["source"], "entities": [{"text": ent.text, "label": ent.label_} for ent in doc.ents]})
    return results

# Применяем модель к новым данным
model_results = apply_model(all_texts, "./output/model-best")
with open("model_results.json", "w", encoding="utf-8") as f:
    json.dump(model_results, f, ensure_ascii=False, indent=4)

print("Разметка завершена. Результаты сохранены в 'model_results.json'.")

# Загрузка данных
with open("annotated_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Преобразование формата
converted_data = []
for idx, entry in enumerate(data):
    paragraphs = {
        "text": entry["text"],
        "entities": [
            {"start": start, "end": end, "label": label}
            for start, end, label in entry["entities"]
        ]
    }
    converted_data.append({"id": idx, "paragraphs": [paragraphs]})

# Сохранение преобразованных данных
with open("converted_annotated_data.json", "w", encoding="utf-8") as f:
    json.dump(converted_data, f, ensure_ascii=False, indent=4)

print("Данные преобразованы и сохранены в 'converted_annotated_data.json'")