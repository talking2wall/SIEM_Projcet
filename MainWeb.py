from flask import Flask, request, jsonify, render_template
import pandas as pd
import AnomalyDetection
import MLDetection
import CheckForAlerts
import CreateNewAlert
import Filter
import DashboardGraphics
import splunklib.client as client
import splunklib.results as results
import psutil
import json


app = Flask(__name__)


def extract_data_for_update(df):
    # simply extract all the alerts
    alerts_list = CheckForAlerts.Run(df, '1999-01-01', '2030-01-01')
    # creating the plots and returning the page
    pies_data, pies_data_titles = DashboardGraphics.get_pie_data(df)
    plot_divs, plot_divs_titles = DashboardGraphics.create_time_series_plots(df)
    img_data_base64_list = DashboardGraphics.generate_pie_chart(pies_data)

    return pies_data, pies_data_titles, plot_divs, plot_divs_titles, img_data_base64_list, alerts_list


@app.route('/update_data')
def update_data():
    global online_status

    if online_status:
        df = pd.read_csv('realtime_db.csv')  # Update the file path as needed
    else:
        df = pd.read_csv('dataframes/good_samples_cleaned.csv')  # Update the file path as needed

    # Extract the data for updating the charts and table
    pies_data, pies_data_titles, plot_divs, plot_divs_titles, img_data_base64_list, alerts_list = extract_data_for_update(df)

    data = {
        'pieData': pies_data,
        'pieDataTitles': pies_data_titles,
        'plotDivs': plot_divs,
        'plotDivsTitles': plot_divs_titles,
        'pieImgData': img_data_base64_list,
        'alertsList': alerts_list,
    }
    return jsonify(data)

@app.route('/')
def index():
    global online_status
    if online_status == True:
        df = pd.read_csv(r'realtime_db.csv')
        df_bad = df
    else:
        # load good samples for the graphs
        df = pd.read_csv(r'dataframes\good_samples_cleaned.csv')
        # load good samples for the alerts table
        df_bad = pd.read_csv(r'dataframes\bad_login_cleaned.csv')

    # simply extract all the alerts
    alerts_list = CheckForAlerts.Run(df_bad, '1999-01-01', '2030-01-01')
    # creating the plots and returning the page
    pies_data, pies_data_titles = DashboardGraphics.get_pie_data(df)
    plot_divs, plot_divs_titles = DashboardGraphics.create_time_series_plots(df)
    img_data_base64_list = DashboardGraphics.generate_pie_chart(pies_data)
    return render_template('index.html', alerts_list=alerts_list, pie_data=img_data_base64_list, plot_divs=plot_divs, pies_data_titles=pies_data_titles, plot_divs_titles=plot_divs_titles, online_status=online_status)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get the values from the form
        dropdown_values = request.form.getlist('dropdown[]')
        textbox_values = request.form.getlist('textbox[]')
        # load the dataframe
        if online_status == True:
            df = pd.read_csv(r'realtime_db.csv')
        else:
            df = pd.read_csv(r'dataframes\good_samples_cleaned.csv')
        df['Message'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)
        # remove the first two items of the template filter (caused of html filter row implemetation)
        textbox_values.pop(0)
        textbox_values.pop(0)
        # Filtering the data and returning the result
        df_detections_filtered = Filter.Filter(df, dropdown_values, textbox_values)
        df_detections_filtered_html = df_detections_filtered.to_html(classes='table table-striped table-bordered')
        return jsonify(table=df_detections_filtered_html)

    return render_template('search.html')

@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':
        # Retrieve the date values from the form data
        start_date = request.form.get('startDateInput')
        end_date = request.form.get('endDateInput')
        # load the dataframe
        if online_status == True:
            df = pd.read_csv(r'realtime_db.csv')
        else:
            df = pd.read_csv(r'dataframes\bad_login_cleaned.csv')
        # check for alert and return the results
        alerts_list = CheckForAlerts.Run(df, start_date, end_date)
        return jsonify(alerts_list)
    else:
        if online_status == True:
            df = pd.read_csv(r'realtime_db.csv')
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
        if online_status == True:
            df = pd.read_csv(r'realtime_db.csv')
        else:
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
        if online_status == True:
            df = pd.read_csv(r'realtime_db.csv')
        else:
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

    online_status = False
    # Check if the realtime script is running to determine what dataframes to use
    def is_script_running(script_name):
        for process in psutil.process_iter(attrs=['cmdline']):
            try:
                cmdline = process.info['cmdline']
                if cmdline and "python" in cmdline[0].lower() and script_name in " ".join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    if is_script_running("realtime_logger.py") == True:
        online_status = True

    app.run(debug=True)