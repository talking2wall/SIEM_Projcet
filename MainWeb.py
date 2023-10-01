from flask import Flask, request, jsonify, render_template
import pandas as pd
import AnomalyDetection
import MLDetection
import CheckForAlerts
import CreateNewAlert

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
        return jsonify(alerts_list)
    else:
        df = pd.read_csv(r'dataframes\bad_login_cleaned.csv')
        alerts_list = CheckForAlerts.Run(df)
        return render_template('alerts.html', alerts_list=alerts_list)
    
@app.route('/create-new-alert', methods=['GET', 'POST'])
def create_new_alert():
    if request.method == 'POST':
        # Get the values from the form
        dropdown_values = request.form.getlist('dropdown[]')
        textbox_values = request.form.getlist('textbox[]')
        file_name = request.form.get('file-name')
        alert_message = request.form.get('alert-message')
        severity_level = request.form.get('severity_dropdown')

        # validate input
        if len(dropdown_values) == 0 or len(textbox_values) == 0:
            return render_template('create-new-alert.html', OperationSuccessful = False, Message ='Error: Please fill one or more filters.')

        OperationMessage = CreateNewAlert.CreateAlert(dropdown_values, textbox_values, file_name, alert_message, severity_level)

        if (OperationMessage == 'Successful'):
            return render_template('create-new-alert.html', OperationSuccessful = True, Message = 'Alert created successfuly!')
        else:
            return render_template('create-new-alert.html', OperationSuccessful = False, Message = OperationMessage)
    else:
        return render_template('create-new-alert.html', OperationSuccessful = False)
    
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