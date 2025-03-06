import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import Dataset, DataLoader
import os
import json
import numpy as np

# Charger les intents depuis le fichier JSON
json_path = os.path.join(os.path.dirname(__file__), 'intent.json')
print("Chemin du fichier JSON:", json_path)  # Afficher le chemin
with open(json_path, 'r', encoding='utf-8') as file:
    intents = json.load(file)

# Préparer les données d'entraînement
class IntentDataset(Dataset):
    def __init__(self, intents, tokenizer, max_length=128):
        self.intents = intents
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.texts = []
        self.labels = []

        # Associer chaque tag à un index
        self.tag_to_index = {intent['tag']: i for i, intent in enumerate(intents['intents'])}
        self.index_to_tag = {i: intent['tag'] for i, intent in enumerate(intents['intents'])}

        # Préparer les données
        for intent in intents['intents']:
            for pattern in intent['patterns']:
                self.texts.append(pattern)
                self.labels.append(self.tag_to_index[intent['tag']])

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(text, return_tensors='pt', max_length=self.max_length, padding='max_length', truncation=True)
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

# Charger le tokenizer et le modèle BERT
tokenizer = BertTokenizer.from_pretrained('distilbert-base-uncased')
model = BertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(intents['intents']))

# Préparer le dataset et le dataloader
dataset = IntentDataset(intents, tokenizer)
dataloader = DataLoader(dataset, batch_size=30, shuffle=True)

# Entraîner le modèle
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
optimizer = AdamW(model.parameters(), lr=2e-5)

# Boucle d'entraînement
epochs = 30
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch in dataloader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    print(f'Epoch {epoch + 1}, Loss: {total_loss / len(dataloader)}')

# Fonction pour classer un message utilisateur
def classify_message(user_input):
    inputs = tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_index = torch.argmax(outputs.logits).item()
    predicted_tag = dataset.index_to_tag.get(predicted_index, None)

    if predicted_tag:
        for intent in intents['intents']:
            if intent['tag'] == predicted_tag:
                return intent['responses'][0]  # Retourne la première réponse associée au tag

    return "Désolé, je ne comprends pas votre question."