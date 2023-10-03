from flask import Flask, request, jsonify, render_template
import pandas as pd
import AnomalyDetection
import MLDetection
import CheckForAlerts
import CreateNewAlert
import Filter

app = Flask(__name__)

@app.route('/')
def index():
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
        # Loading a dummy dataset
        df = pd.read_csv(r'dataframes\bad_samples_cleaned_port_scanning_reducted.csv')
        df['Message'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)

        # check if user clicked 'Show all results'
        if 'link_clicked' in request.form and request.form['link_clicked'] == 'true':
            df_html = df.to_html(classes='table table-striped table-bordered')
            return jsonify(table=df_html)

        # retrieving parameters from the html page
        threshold_from = float(request.form.get('threshold-from'))
        threshold_to = float(request.form.get('threshold-to'))
        dropdown_values = request.form.getlist('dropdown[]')
        textbox_values = request.form.getlist('textbox[]')

        # remove the first two items of the template filter (caused of html filter row implemetation)
        textbox_values.pop(0)
        textbox_values.pop(0)

        # Running machine learning algorithm
        df_anomalies = AnomalyDetection.Run(df)

        # Filtering the data and returning the result
        dropdown_values.append('AnomalyScore')
        textbox_values.append(float(threshold_from))
        textbox_values.append(float(threshold_to))
        df_anomalies_filtered = Filter.Filter(df_anomalies, dropdown_values, textbox_values)
        df_anomalies_filtered_html = df_anomalies_filtered.to_html(classes='table table-striped table-bordered')
        return jsonify(table=df_anomalies_filtered_html)
    return render_template('anomaly-detection.html')
        
@app.route('/ml-detection', methods=['GET', 'POST'])
def ml_detection():
    if request.method == 'POST':
        # retrieving algorithm parameter
        detector_algorithm = request.form.get('dropdown-detector')
        if detector_algorithm == None: # if true, this means the request sent by the 'Show all results' button
            detector_algorithm = request.form.get('algorithm')

        # Loading a dummy dataset
        if detector_algorithm == 'Port Scanning Detector':
            df = pd.read_csv(r'dataframes\bad_samples_cleaned_port_scanning_reducted.csv')
        else:
            df = pd.read_csv(r'dataframes\good_samples_cleaned.csv')
        df['Message'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)

        # check if user clicked 'Show all results'
        if 'link_clicked' in request.form and request.form['link_clicked'] == 'true':
            df_html = df.to_html(classes='table table-striped table-bordered')
            return jsonify(table=df_html)
            
        # retrieving parameters from the html page
        detector_algorithm = request.form.get('dropdown-detector')
        threshold = float(request.form.get('threshold'))
        dropdown_values = request.form.getlist('dropdown[]')
        textbox_values = request.form.getlist('textbox[]')

        # remove the first two items of the template filter (caused of html filter row implemetation)
        textbox_values.pop(0)
        textbox_values.pop(0)

        # Running machine learning algorithm
        df_detections = MLDetection.Run(df, threshold, detector_algorithm)
        df_detections = df_detections[df_detections['IsMalicious'] == 'Yes']

        # Filtering the data and returning the result
        df_detections_filtered = Filter.Filter(df_detections, dropdown_values, textbox_values)
        df_detections_filtered_html = df_detections_filtered.to_html(classes='table table-striped table-bordered')
        return jsonify(table=df_detections_filtered_html)

    return render_template('ml-detection.html')

if __name__ == "__main__":
    app.run(debug=True)