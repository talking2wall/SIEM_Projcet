import yaml
import pandas as pd
import os
from datetime import datetime, time

def process_alert_config(df):
    paths, configs = load_files()

    # if there is a time rule, check that the rule was wrote correctly
    for i, cfg in enumerate(configs):
        if (('start_time' in cfg['parameters'].keys() and 'end_time' not in cfg['parameters'].keys()) or
            ('end_time' in cfg['parameters'].keys() and 'start_time' not in cfg['parameters'].keys())):
            raise KeyError('Missing \'start_time\' or \'end_time\' in yaml file: ', paths[i])

    # go for each rule and filter unmatched rows
    for cfg in configs:
        time_filter = False
        count_filter = -1
        df_result = df.copy() # reload the dataframe
        for column, rule in cfg['parameters'].items():
            if column == 'count':
                count_filter = rule
                continue
            if column == 'start_time':
                time_filter = True
                start_time = datetime.strptime(rule, '%H:%M:%S').time()
                continue
            if column == 'end_time':
                time_filter = True
                end_time = datetime.strptime(rule, '%H:%M:%S').time()
                continue

            df_result = df_result[df_result[column] == rule]

        if time_filter == True:
            if start_time > end_time:
                df_after = df_result[(df_result['Time'] >= start_time.strftime('%H:%M:%S'))]
                df_before = df_result[df_result['Time'] <= end_time.strftime('%H:%M:%S')]
                df_result = pd.concat([df_after, df_before])
            else:
                df_result = df_result[(df_result['Time'] >= start_time.strftime('%H:%M:%S')) &
                                      (df_result['Time'] <= end_time.strftime('%H:%M:%S'))]

        # print rows left after filtering
        if type(count_filter) == int and count_filter > 0:
            for i in range(0, int(len(df_result) / count_filter)):
                print('Alert Found:', cfg['alert']['Message'])
                print('Severity Level:', cfg['alert']['SeverityLevel'])
        else:
            for i in range(0, len(df_result)):
                print('Alert Found:', cfg['alert']['Message'])
                print('Severity Level:', cfg['alert']['SeverityLevel'])


def convert_time_to_unit(time_str):
    pass


def load_files():
    yaml_config_list = []
    yaml_config_file_paths = []
    # Iterate through all YAML files in the configs/alerts directory
    for root, dirs, files in os.walk(r'configs\alerts'):
        for file in files: 
            if file.endswith('.yaml') or file.endswith('.yml'):
                path = os.path.join(root, file)
                yaml_config_file_paths.append(path)
                yaml_file_content = read_yaml(path)
                if (yaml_file_content != None):
                    yaml_config_list.append(yaml_file_content)
    return yaml_config_file_paths, yaml_config_list # return a list contains all the yaml files content
        
            
def read_yaml(path):
    try:
        with open(path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        print(f"Error loading YAML file {path}: {str(e)}")
        return None
    

df = pd.read_csv(r'dataframes\good_login_cleaned.csv')
process_alert_config(df)