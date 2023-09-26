from flask import Flask, request, jsonify, render_template
import pandas as pd
import AnomalyDetection
import MLDetection

app = Flask(__name__)

@app.route('/')
def index():
    # Replace this with your Pandas DataFrame
    # data = {
    #     "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
    #     "Age": [30, 25, 35],
    #     "City": ["New York", "Los Angeles", "Chicago"]
    # }
    df = pd.read_csv('good_samples_cleaned.csv')
    return render_template('index.html', table=df.to_html(classes='table table-striped'))

@app.route('/anomaly-detection', methods=['GET', 'POST'])
def anomaly_detection():
    if request.method == 'POST':
        threshold = float(request.form['threshold'])
        df = pd.read_csv('bad_samples_cleaned.csv')
        df_anomalies = AnomalyDetection.Run(df, threshold)
        # Convert the filtered data to HTML for rendering in the table
        df_anomalies_filtered = df_anomalies.to_html(classes='table table-striped table-bordered')
        # Return the filtered DataFrame as JSON response
        return jsonify(table=df_anomalies_filtered)
    return render_template('anomaly-detection.html')
        
@app.route('/ml-detection', methods=['GET', 'POST'])
def ml_detection():
    if request.method == 'POST':
        threshold = float(request.form['threshold'])
        df = pd.read_csv('bad_samples_cleaned.csv')
        df_detections = MLDetection.Run(df, threshold)
        df_detections = df_detections[df_detections['IsMalicious'] == 'Yes']
        # Convert the filtered data to HTML for rendering in the table
        df_detections_filtered = df_detections.to_html(classes='table table-striped table-bordered')
        # Return the filtered DataFrame as JSON response
        return jsonify(table=df_detections_filtered)
    return render_template('ml-detection.html')


if __name__ == "__main__":
    app.run(debug=True)