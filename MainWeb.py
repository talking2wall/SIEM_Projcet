from flask import Flask, request, jsonify, render_template
import pandas as pd
import AnomalyDetection
import MLDetection
import CheckForAlerts

app = Flask(__name__)

@app.route('/')
def index():
    # Replace this with your Pandas DataFrame
    # data = {
    #     "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
    #     "Age": [30, 25, 35],
    #     "City": ["New York", "Los Angeles", "Chicago"]
    # }
    df = pd.read_csv(r'dataframes\good_samples_cleaned.csv')
    return render_template('index.html', table=df.to_html(classes='table table-striped'))

@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':
        # Retrieve the date values from the form data
        start_date = request.form.get('startDateInput')
        end_date = request.form.get('endDateInput')
        df = pd.read_csv(r'dataframes\bad_login_cleaned.csv')
        alerts_list = CheckForAlerts.Run(df, start_date, end_date)
        print(alerts_list)
        return jsonify(alerts_list)
    else:
        df = pd.read_csv(r'dataframes\bad_login_cleaned.csv')
        alerts_list = CheckForAlerts.Run(df)
        return render_template('alerts.html', alerts_list=alerts_list)
    
@app.route('/create-new-alert', methods=['GET', 'POST'])
def create_new_alert():
    if request.method == 'POST':
        # start_date = request.form.get('startDateInput')
        # end_date = request.form.get('endDateInput')
        
        return render_template('create-new-alert.html', log_added_successfuly='True')
    else:
        return render_template('create-new-alert.html', log_added_successfuly='False')
    
@app.route('/anomaly-detection', methods=['GET', 'POST'])
def anomaly_detection():
    if request.method == 'POST':
        threshold = float(request.form['threshold'])
        df = pd.read_csv(r'dataframes\bad_login_cleaned.csv')
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
        df = pd.read_csv(r'dataframes\bad_samples_cleaned.csv')
        df_detections = MLDetection.Run(df, threshold)
        df_detections = df_detections[df_detections['IsMalicious'] == 'Yes']
        # Convert the filtered data to HTML for rendering in the table
        df_detections_filtered = df_detections.to_html(classes='table table-striped table-bordered')
        # Return the filtered DataFrame as JSON response
        return jsonify(table=df_detections_filtered)
    return render_template('ml-detection.html')


if __name__ == "__main__":
    app.run(debug=True)