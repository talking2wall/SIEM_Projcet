import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

def Run(df, threshold, model):
    
    df_original = df.copy()

    model_path = ''
    if model == 'File Encryption Detector':
        model_path = r'models\file-encryption-logistic_regression_model.pkl'
    elif model == 'Port Scanning Detector':
        model_path = r'models\port-scanning-logistic_regression_model.pkl'

    with open(model_path, 'rb') as f:
        vectorizer, model = pickle.load(f)

    log_message = df['Message']
    log_messages_vectorized = vectorizer.transform(log_message)
    predicted_probabilities = model.predict_proba(log_messages_vectorized)
    isMalicious = ['Yes' if x[1] > threshold else 'No' for x in predicted_probabilities]
    df_original['IsMalicious'] = isMalicious

    return df_original