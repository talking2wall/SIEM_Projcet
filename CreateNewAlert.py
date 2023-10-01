import yaml
import os

def create_dict(properties):
    result_dict = {}
    for prop, value in properties:
        result_dict[prop] = value
    return result_dict

def CreateAlert(dropdown_values, textbox_values, file_name, alert_message, severity_level):

    OperationMessage = 'Successful'
    try:
        # fix file name
        if (not file_name.endswith('.yml') or not file_name.endswith('.yaml')):
            file_name = file_name + '.yml'
        
        # parse the data and create a list of parameter-value pairs
        j = 0
        parameter_properties = []
        for i in range(0, len(dropdown_values)):
            if dropdown_values[i] == 'Time':
                parameter_properties.append(('start_time', str(textbox_values[j])))
                parameter_properties.append(('end_time', str(textbox_values[j+1])))
            elif dropdown_values[i] in ['EventType', 'Type', 'RecordNumber', 'EventCode']:
                parameter_properties.append((dropdown_values[i], int(textbox_values[j])))
            else:
                parameter_properties.append((dropdown_values[i], str(textbox_values[j])))
            j = j + 2

        alert_properties = [
            ('Message', alert_message),
            ('SeverityLevel', severity_level)
        ]

        # Create dictionaries for parameters and alert
        parameter_dict = create_dict(parameter_properties)
        alert_dict = create_dict(alert_properties)

        data = {
            'alert': alert_dict,
            'parameters': parameter_dict
        }

        # Write the data to the YAML file
        file_name = os.path.join(r'configs\alerts', file_name)
        with open(file_name, "w") as file:
            yaml.dump(data, file, default_flow_style=False)
    
    except Exception as ex:
        OperationMessage = ex

    return OperationMessage