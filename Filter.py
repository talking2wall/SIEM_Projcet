def Filter(df, dropdown_values, textbox_values):
    
    df_result = df.copy()

    j = 0
    for i in range(0, len(dropdown_values)):
        if (dropdown_values[i] == 'Date' or dropdown_values[i] == 'Time'):
            df_result = df_result[df_result[dropdown_values[i]] >= textbox_values[j]]
            df_result = df_result[df_result[dropdown_values[i]] <= textbox_values[j+1]]
        elif dropdown_values[i] in ['EventType', 'Type', 'RecordNumber', 'EventCode']:
            df_result = df_result[df_result[dropdown_values[i]] == int(textbox_values[j])]
        else:
            df_result = df_result[df_result[dropdown_values[i]] == textbox_values[j]]
        
        j = j + 2

    print(len(df_result))

    return df_result