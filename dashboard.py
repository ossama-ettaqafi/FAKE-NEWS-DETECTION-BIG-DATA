# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request
from cassandra.cluster import Cluster
import pandas as pd
import joblib
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from config.settings import (
    CASSANDRA_HOST,
    CASSANDRA_KEYSPACE,
    CASSANDRA_PREDICTIONS_TABLE,
    CASSANDRA_EVALUATION_TABLE,
    TFIDF_MODEL_PATH,
    NAIVE_BAYES_MODEL_PATH,
    SVM_MODEL_PATH
)

# Flask app setup: specify templates and static folders inside 'dashboard' folder
app = Flask(
    __name__,
    template_folder=os.path.join('dashboard', 'templates'),
    static_folder=os.path.join('dashboard', 'static')
)

# Cassandra connection setup
cluster = Cluster([CASSANDRA_HOST])
session = cluster.connect(CASSANDRA_KEYSPACE)

# Load models once at startup
tfidf = joblib.load(TFIDF_MODEL_PATH)
nb_model = joblib.load(NAIVE_BAYES_MODEL_PATH)
svm_model = joblib.load(SVM_MODEL_PATH)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    text = text.encode('ascii', 'ignore').decode()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    rows = session.execute(f'SELECT * FROM {CASSANDRA_PREDICTIONS_TABLE}')
    df_preds = pd.DataFrame(list(rows))

    rows_eval = session.execute(f'SELECT * FROM {CASSANDRA_EVALUATION_TABLE}')
    df_eval = pd.DataFrame(list(rows_eval))

    total_predictions = len(df_preds)
    correct_predictions = (df_preds['label'] == df_preds['prediction']).sum() if total_predictions > 0 else 0
    global_accuracy = round((correct_predictions / total_predictions) * 100, 2) if total_predictions > 0 else 0
    real_count = (df_preds['label'] == 0).sum() if total_predictions > 0 else 0
    fake_count = (df_preds['label'] == 1).sum() if total_predictions > 0 else 0

    model_stats = []
    if not df_preds.empty:
        for model in df_preds['model'].unique():
            df_model = df_preds[df_preds['model'] == model]
            total = len(df_model)
            correct = (df_model['label'] == df_model['prediction']).sum()
            acc = round(correct / total * 100, 2) if total > 0 else 0
            model_stats.append({
                'model': model,
                'total': total,
                'correct': correct,
                'accuracy': acc
            })

    new_prediction = None
    user_text = ""
    model_used = ""

    if request.method == 'POST':
        user_text = request.form.get('news_text', '').strip()
        model_choice = request.form.get('model_choice', 'naive_bayes')

        if user_text:
            clean_text = preprocess(user_text)
            vec = tfidf.transform([clean_text])

            if model_choice == "svm":
                prediction = svm_model.predict(vec)[0]
                model_used = "SVM"
            else:
                prediction = nb_model.predict(vec)[0]
                model_used = "Naive Bayes"

            new_prediction = "Fake News" if prediction == 1 else "Real News"

    return render_template('dashboard.html',
                           total_predictions=total_predictions,
                           correct_predictions=correct_predictions,
                           global_accuracy=global_accuracy,
                           real_count=real_count,
                           fake_count=fake_count,
                           metrics=df_eval.to_dict(orient='records'),
                           model_stats=model_stats,
                           new_prediction=new_prediction,
                           model_used=model_used,
                           user_text=user_text)

if __name__ == '__main__':
    app.run(debug=True)
