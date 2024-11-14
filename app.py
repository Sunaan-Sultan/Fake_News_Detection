from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import requests
from transformers import BertTokenizer, TFBertModel
from tensorflow.keras.models import load_model
from tcn import TCN
import spacy
from flask_mail import Mail, Message
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dev1925004@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'dev1925004@gmail.com'

mail = Mail(app)

# Google Custom Search API key and Search Engine ID
# GOOGLE_API_KEY = 'AIzaSyAEv4CDKFE5SiKvGZndnz9A275PJx6l634'
# SEARCH_ENGINE_ID = '20378757f8a1d40f7'

GOOGLE_API_KEY = 'AIzaSyAz_2nfxi0kgF9uqRpmDCXNbyEkEui2cOo'
SEARCH_ENGINE_ID = '20378757f8a1d40f7'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load the BERT-TCN model
custom_objects = {'TFBertModel': TFBertModel, 'TCN': TCN}
model = load_model('best_model.h5', custom_objects=custom_objects)

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
        padding='max_length',
        return_attention_mask=True,
        return_tensors='tf',
    )
    return {
        'input_ids': encoded['input_ids'],
        'attention_mask': encoded['attention_mask']
    }

# Function to extract key entities and phrases
def extract_key_phrases_and_entities(text, num_phrases=5):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]

    tfidf_vectorizer = TfidfVectorizer(
        max_df=1.0,
        min_df=1,
        stop_words='english',
        max_features=10000,
        ngram_range=(1, 3)
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])
    phrases = tfidf_vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    phrase_score_pairs = list(zip(phrases, scores))
    sorted_phrases = sorted(phrase_score_pairs, key=lambda x: x[1], reverse=True)
    key_phrases = [phrase for phrase, score in sorted_phrases[:num_phrases]]

    return entities + key_phrases

def generate_query(text):
    return text.strip().split('\n')[0]  # Return the first line as the query

def fetch_related_articles(query):
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&num=5'
    response = requests.get(url)
    articles = []

    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
            articles.append({
                'title': item.get('title'),
                'url': item.get('link'),
                'snippet': item.get('snippet', 'No description available')
            })
    else:
        articles.append({'title': 'No articles found', 'url': '#', 'snippet': 'Try a different query.'})
    return articles

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        text = request.form['text']
        first_line = text.strip().split('\n')[0]  # Extract the first line as the title
        preprocessed_text = preprocess_input(text)

        prediction = model.predict([preprocessed_text['input_ids'], preprocessed_text['attention_mask']])[0][0]
        print(f'Prediction value: {prediction}')

        if prediction <= 0.3:
            pred_label = 'False News'
        elif 0.3 < prediction <= 0.44:
            pred_label = 'Mostly False'
        elif 0.44 < prediction <= 0.55:
            pred_label = 'Half True'
        elif 0.55 < prediction <= 0.75:
            pred_label = 'Mostly True'
        else:
            pred_label = 'True News'

        query = generate_query(first_line)
        print(query)
        related_articles = fetch_related_articles(query)

        return jsonify({'prediction': pred_label, 'evidence': related_articles})
    else:
        return jsonify({'prediction': 'Something went wrong'})

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    feedback = request.form['feedback']
    app.logger.debug(f'Received feedback: {feedback}')
    msg = Message(
        subject="New Feedback Received",
        recipients=['sunaansultan5@gmail.com'],
        body=f"Feedback: {feedback}"
    )
    try:
        mail.send(msg)
        app.logger.debug('Feedback sent successfully!')
        return jsonify({'status': 'Feedback sent successfully!'})
    except Exception as e:
        app.logger.error(f"Error sending email: {e}")
        return jsonify({'status': 'Failed to send feedback.'})

if __name__ == '__main__':
    app.run(debug=True)
