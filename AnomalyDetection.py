import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

def Run(df, threshold):
    
    ########################
    ### pre-proccessing  ###
    ########################

    # Save the original dataframe
    df_original = df.copy()

    # Encode Date
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    # ENcode Time
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce')
    df['Hour'] = df['Time'].dt.hour
    df['Minute'] = df['Time'].dt.minute
    df['Second'] = df['Time'].dt.second
    # Remove Date & Time
    df.drop(['Date','Time'], axis=1, inplace=True)
    # Initialize a LabelEncoder
    label_encoder = LabelEncoder()
    # Encode all cateforic columns to a numeric value
    df['LogName'] = label_encoder.fit_transform(df['LogName'])
    df['Keywords'] = label_encoder.fit_transform(df['Keywords'])
    df['TaskCategory'] = label_encoder.fit_transform(df['TaskCategory'])
    df['SourceName'] = label_encoder.fit_transform(df['SourceName'])
    df['OpCode'] = label_encoder.fit_transform(df['OpCode'])
    df['ComputerName'] = label_encoder.fit_transform(df['OpCode'])
    # Initialize CountVectorizer
    vectorizer = CountVectorizer(max_features=1000, stop_words='english')
    # Fit and transform the 'Message' column
    message_bow = vectorizer.fit_transform(df['Message'])
    # Convert the bag of words representation to a DataFrame
    message_df = pd.DataFrame(message_bow.toarray(), columns=vectorizer.get_feature_names_out())
    # Add the BoW representation as new columns in your original DataFrame
    df = pd.concat([df, message_df], axis=1)
    # Delete 'Message' column
    df.drop(['Message'], axis=1, inplace=True)
    
    ############################
    ### predicting the data  ###
    ############################

    # Create and train the Isolation Forest model
    model = IsolationForest(contamination=0.05, random_state=42)  # You can adjust the contamination parameter
    model.fit(df)

    # Predict anomaly scores for each data point
    anomaly_scores = model.decision_function(df)

    # Add the anomaly scores as a new column in your DataFrame
    df_original['AnomalyScore'] = anomaly_scores

    # Identify anomalies based on a threshold (you can adjust this threshold)
    anomalies = df_original[df_original['AnomalyScore'] < threshold]

    return anomalies