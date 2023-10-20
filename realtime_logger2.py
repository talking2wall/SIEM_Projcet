import splunklib.client as client
import splunklib.results as results
import pandas as pd
import datetime
import time
import os
import re
from threading import Thread

HOST = "localhost"
PORT = 8089
USERNAME = "Admin"
PASSWORD = "12345678"

# Create a Service instance and log in 
service = client.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD)

if os.path.isfile('realtime_db.csv') == False:
    # create the new dataframe
    LogName = []
    Date = []
    Time = []
    ComputerName = []
    SourceName = []
    TaskCategory = []
    EventType = []
    Message = []
    Keywords = []
    OpCode = []
    EventCode = []
    Type = []
    RecordNumber = []

    df = pd.DataFrame({ 'LogName' : LogName,
                        'Date' : Date,
                        'Time' : Time,
                        'ComputerName' : ComputerName,
                        'SourceName' : SourceName,
                        'TaskCategory' : TaskCategory,
                        'EventType' : EventType,
                        'Keywords' : Keywords,
                        'OpCode' : OpCode,
                        'EventCode' : EventCode,
                        'Type' : Type,
                        'RecordNumber' : RecordNumber,
                        'Message' : Message })
    
    df.to_csv('realtime_db.csv', index=False)
    
else:
    df = pd.read_csv('realtime_db.csv', index_col=False)


time_interval = 5

latest = datetime.datetime.now()
earliest = latest - datetime.timedelta(0,time_interval)


def RunSearch(search_query):
    # Run the search
    job = service.jobs.create(search_query)

    # Get the results
    search_results = job.results(output_mode='json')
    # ValueError: time data "2023-09-22 00:10:15" doesn't match format "%m/%d/%Y %H:%M:%S %p", at position 0. You might want to try:
    reader = results.JSONResultsReader(search_results)
    for result in reader:
        if isinstance(result, dict): # check if the result is a search result and not a search job result such as an informational or error message
            current_log = result['_raw']
            new_row = { 'LogName' : re.search('LogName=(.*)\n', current_log).group(1),
                        'Date' : datetime.datetime.strptime(current_log[0:10], '%m/%d/%Y').strftime('%Y-%m-%d'),
                        'Time' : datetime.datetime.strptime(current_log[11:22], '%I:%M:%S %p').strftime('%H:%M:%S'),
                        'ComputerName' : re.search('ComputerName=(.*)\n', current_log).group(1),
                        'SourceName' : re.search('SourceName=(.*)\n', current_log).group(1),
                        'TaskCategory' : re.search('TaskCategory=(.*)\n', current_log).group(1),
                        'EventType' : re.search('EventType=(.*)\n', current_log).group(1),
                        'Keywords' : re.search('Keywords=(.*)\n', current_log).group(1),
                        'OpCode' : re.search('OpCode=(.*)\n', current_log).group(1),
                        'EventCode' : re.search('EventCode=(.*)\n', current_log).group(1),
                        'Type' : re.search('Type=(.*)\n', current_log).group(1),
                        'RecordNumber' : re.search('RecordNumber=(.*)\n', current_log).group(1),
                        'Message' : re.search('Message=(.*)', current_log).group(1)
            }
            df = pd.DataFrame([new_row])
            # Append the new row to the CSV file
            df.to_csv('realtime_db.csv', mode='a', header=False, index=False)
            print('STATUS: A new log was added:')
            print(new_row)


while True:

    if datetime.datetime.now() >= latest:
        print('set a search for ealiest =', earliest.strftime("%m/%d/%Y:%H:%M:%S"), 'to', latest.strftime("%m/%d/%Y:%H:%M:%S"))
        search_query = f'search index=main earliest=\"{earliest.strftime("%m/%d/%Y:%H:%M:%S")}\" latest=\"{latest.strftime("%m/%d/%Y:%H:%M:%S")}\"'
        thread = Thread(target = RunSearch, args = (search_query, ))
        thread.start()
        thread.join()
        print('Thread from', earliest.strftime("%m/%d/%Y:%H:%M:%S"), 'to', latest.strftime("%m/%d/%Y:%H:%M:%S"), 'has finished.')
        latest = latest + datetime.timedelta(0,time_interval)
        earliest = earliest + datetime.timedelta(0,time_interval)
        
    # print('STATUS: Waiting for incoming data.')
    # time.sleep(0.1)