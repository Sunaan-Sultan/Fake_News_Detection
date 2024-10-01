from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
from tensorflow.keras.models import load_model
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import requests
from tcn import TCN
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dev1925004@gmail.com'  
app.config['MAIL_PASSWORD'] = ''  
app.config['MAIL_DEFAULT_SENDER'] = 'dev1925004@gmail.com'  
app.config['MAIL_SUPPRESS_SEND'] = False  

mail = Mail(app)

NEWS_API_KEY = ''

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load the BERT-TCN model with custom objects for TFBertModel and TCN
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
        padding='max_length',  # Ensure padding to the max_length
        return_attention_mask=True,
        return_tensors='tf',
    )
    return {
        'input_ids': encoded['input_ids'],  # This will be (1, 128)
        'attention_mask': encoded['attention_mask']  # This will be (1, 128)
    }

# Function to extract key entities and phrases
import numpy as np

def extract_key_phrases_and_entities(text, num_phrases=5):
    # Extract named entities using spaCy
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]

    # Use TF-IDF to extract important phrases
    tfidf_vectorizer = TfidfVectorizer(
        max_df=1.0,
        min_df=1,
        stop_words='english',
        max_features=10000,
        ngram_range=(1, 3)
    )

    # Fit the vectorizer and transform the text to get the TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])
    
    # Get feature names (phrases) and their corresponding TF-IDF scores
    phrases = tfidf_vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    
    # Combine phrases with their scores and sort by score
    phrase_score_pairs = list(zip(phrases, scores))
    sorted_phrases = sorted(phrase_score_pairs, key=lambda x: x[1], reverse=True)
    
    # Select the top `num_phrases` phrases based on their scores
    key_phrases = [phrase for phrase, score in sorted_phrases[:num_phrases]]

    # Combine entities and key phrases
    return entities + key_phrases


def generate_query(text):
    key_phrases_and_entities = extract_key_phrases_and_entities(text)
    # Join entities and key phrases into a single search query string
    query = ' '.join(key_phrases_and_entities[:5])  # Limit to 5 items to keep the query concise
    return query

def fetch_related_articles(query):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=5'
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
        preprocessed_text = preprocess_input(text)

        # Make prediction using the BERT-TCN model
        prediction = model.predict([preprocessed_text['input_ids'], preprocessed_text['attention_mask']])[0][0]
        print(f'Prediction value: {prediction}')

        # Classify based on new prediction ranges
        if prediction <= 0.3:
            pred_label = 'False News'
        elif 0.31 <= prediction <= 0.44:
            pred_label = 'Mostly False'
        elif 0.45 <= prediction <= 0.55:
            pred_label = 'Half True'
        elif 0.56 <= prediction <= 0.75:
            pred_label = 'Mostly True'
        else:
            pred_label = 'True News'

        # Generate a query using key phrases and entities extracted from the text
        query = generate_query(text)

        # Fetch related articles using the generated query
        related_articles = fetch_related_articles(query)

        return jsonify({'prediction': pred_label, 'evidence': related_articles})
    else:
        return jsonify({'prediction': 'Something went wrong'})
                    

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    feedback = request.form['feedback']
    app.logger.debug(f'Received feedback: {feedback}')
    # Create the email message
    msg = Message(
        subject="New Feedback Received",
        recipients=['sunaansultan5@gmail.com'],  # The recipient's email address
        body=f"Feedback: {feedback}"
    )
    try:
        # Send the email
        mail.send(msg)
        app.logger.debug('Feedback sent successfully!')
        return jsonify({'status': 'Feedback sent successfully!'})
    except Exception as e:
        app.logger.error(f"Error sending email: {e}")
        return jsonify({'status': 'Failed to send feedback.'})
    
if __name__ == '__main__':
    app.run(debug=True)

