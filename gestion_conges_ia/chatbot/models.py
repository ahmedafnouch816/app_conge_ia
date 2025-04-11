# chatbot/classifier.py
import os
import json
import torch
import warnings
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Suppress transformers warnings
warnings.filterwarnings("ignore")

# Load intents
json_path = os.path.join(os.path.dirname(__file__), 'intent.json')
with open(json_path, 'r', encoding='utf-8') as file:
    intents = json.load(file)

# Load tokenizer and model (DistilBERT only)
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(intents['intents']))
model.eval()

# Map tag index
tag_to_index = {intent['tag']: i for i, intent in enumerate(intents['intents'])}
index_to_tag = {i: intent['tag'] for i, intent in enumerate(intents['intents'])}

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def classify_message(user_input):
    inputs = tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
    predicted_index = torch.argmax(outputs.logits).item()
    predicted_tag = index_to_tag.get(predicted_index, None)

    if predicted_tag:
        for intent in intents['intents']:
            if intent['tag'] == predicted_tag:
                return intent['responses'][0]
    return "Désolé, je ne comprends pas votre question."
