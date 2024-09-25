from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
from tensorflow.keras.models import load_model
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.model_selection import train_test_split
from tcn import TCN
import requests
import spacy
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

NEWS_API_KEY = '45a02f09ffc4451c9876dcd61c7bbb6a'

# Load the BERT-TCN model with custom objects for TFBertModel and TCN
custom_objects = {'TFBertModel': TFBertModel, 'TCN': TCN}
model = load_model('bert_transformer_attention_model.h5', custom_objects=custom_objects)

# Load the BERT tokenizer
bt_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load spaCy model for key phrase extraction
nlp = spacy.load("en_core_web_sm")

def preprocess_input(news, max_length=128):
    encoded = bt_tokenizer.encode_plus(
        news,
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding='max_length',  # Ensure padding to the max_length
        return_attention_mask=True,
        return_tensors='tf',
    )
    return {
        'input_ids': encoded['input_ids'],  # This will be (1, 128)
        'attention_mask': encoded['attention_mask']  # This will be (1, 128)
    }


# Function to extract the first 5 words from the input news text
def extract_first_few_words(news, num_words=5):
    return ' '.join(news.split()[:num_words])  # Extract first 'num_words' words

    
def fetch_related_articles(query):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = []
    
    if response.status_code == 200:
        data = response.json()
        for article in data['articles']:
            articles.append({
                'title': article['title'],
                'url': article['url'],
                'snippet': article['description'] or 'No description available'
            })
    return articles


# Get BERT embedding for similarity calculation
def get_embedding(text):
    encoded_input = bt_tokenizer(
        text, 
        return_tensors='tf', 
        truncation=True, 
        max_length=128, 
        padding=True
    )
    # Pass only input_ids and attention_mask, ignoring token_type_ids
    output = model([encoded_input['input_ids'], encoded_input['attention_mask']])
    return output.last_hidden_state[:, 0, :]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        text = request.form['text']
        preprocessed_text = preprocess_input(text)

        # Make prediction using the BERT-TCN model
        prediction = model.predict([preprocessed_text['input_ids'], preprocessed_text['attention_mask']])
        pred_label = 'FAKE' if prediction < 0.5 else 'REAL'

        # Extract the first few words from the news text to improve article search
        query = extract_first_few_words(text, num_words=5)

        # Fetch related articles using the extracted query
        related_articles = fetch_related_articles(query)

        return jsonify({'prediction': pred_label, 'evidence': related_articles})
    else:
        return jsonify({'prediction': 'Something went wrong'})


if __name__ == '__main__':
    app.run(debug=True)

# # tfvect = TfidfVectorizer(stop_words='english', max_df=0.7)
# tfvect = pickle.load(open('vectorizer.pkl', 'rb'))
# loaded_model = pickle.load(open('92_DT_model.pkl', 'rb'))
# data = pd.read_csv('WELFake_Dataset.csv')


# def fake_news_det(news):
#     # tfid_x_train = tfvect.fit_transform(x_train)
#     # tfid_x_test = tfvect.transform(x_test)
#     input_data = [news]
#     vectorized_input_data = tfvect.transform(input_data)
#     prediction = loaded_model.predict(vectorized_input_data)
#     return prediction[0]

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     if request.method == 'POST':
#         text = request.form['text']
#         pred = fake_news_det(text)
#         print(pred)
#         return jsonify({'prediction': pred})  # Return prediction as JSON
#     else:
#         return jsonify({'prediction': 'Something went wrong'})  # Return error as JSON

# if __name__ == '__main__':
#     app.run(debug=True)