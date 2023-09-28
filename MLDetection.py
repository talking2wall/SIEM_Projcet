import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

def Run(df, threshold):
    
    df_original = df.copy()
    #df_original['IsMalicious'] = ''

    with open(r'models\logistic_regression_model.pkl', 'rb') as f:
        vectorizer, model = pickle.load(f)

    log_message = df['Message']
    log_messages_vectorized = vectorizer.transform(log_message)
    predicted_probabilities = model.predict_proba(log_messages_vectorized)
    isMalicious = ['Yes' if x[1] > threshold else 'No' for x in predicted_probabilities]
    df_original['IsMalicious'] = isMalicious
    #for i, prob_scores in enumerate(predicted_probabilities):
        #is_malicious = prob_scores[1]  # Probability of being malicious (IsMalicious=1)
        
        # if is_malicious >= threshold:
        #     #df_original['IsMalicious'].iloc[i] = 'Yes'
        #     #df_original.set_value('IsMalicious', i, 'Yes')
        #     df_original.loc['IsMalicious', i] = 'Yes'
        # else:
        #     df_original.loc['IsMalicious', i] = 'No'
        #     #df_original.set_value('IsMalicious', i, 'No')
        #     #df_original['IsMalicious'].iloc[i] = 'No'
    return df_original


    ########################
    ### pre-proccessing  ###
    ########################


