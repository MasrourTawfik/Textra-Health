from transformers import AutoTokenizer, AutoModel
import torch

# Charger le tokenizer et le modèle
model_name = "ilyass20/multilingual-e5-large-MedAnalyser"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Texte d'entrée
text = "Ceci est une phrase d'exemple à tester avec le modèle."

# Encoder le texte
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    outputs = model(**inputs)

# Extraire les embeddings (par exemple, le dernier état caché)
embeddings = outputs.last_hidden_state

print("Embeddings shape:", embeddings.shape)
