from flask import Flask, render_template, request
from cassandra.cluster import Cluster
import pandas as pd
import random

app = Flask(__name__)

# Cassandra connection
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('fakenews')

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    # Get predictions
    rows = session.execute('SELECT * FROM predictions_streaming')
    df_preds = pd.DataFrame(list(rows))

    # Get evaluations
    rows_eval = session.execute('SELECT * FROM evaluation_streaming')
    df_eval = pd.DataFrame(list(rows_eval))

    total_predictions = len(df_preds)
    correct_predictions = (df_preds['label'] == df_preds['prediction']).sum()
    global_accuracy = round((correct_predictions / total_predictions) * 100, 2) if total_predictions > 0 else 0

    real_count = (df_preds['label'] == 0).sum()
    fake_count = (df_preds['label'] == 1).sum()

    new_prediction = None
    user_text = ""

    if request.method == 'POST':
        user_text = request.form.get('news_text')
        if user_text:
            # Simple Fake/Real prediction aléatoire temporaire
            new_prediction = random.choice(["Real News", "Fake News"])

    return render_template('dashboard.html',
                           total_predictions=total_predictions,
                           correct_predictions=correct_predictions,
                           global_accuracy=global_accuracy,
                           real_count=real_count,
                           fake_count=fake_count,
                           metrics=df_eval.to_dict(orient='records'),
                           new_prediction=new_prediction,
                           user_text=user_text)

if __name__ == '__main__':
    app.run(debug=True)
