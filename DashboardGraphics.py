import base64
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from io import BytesIO
import pandas as pd

def get_pie_data(df):
    pie_data = []
    pie_data_titles = []
    titles = ["LogName", "TaskCategory", "OpCode"]

    for i, title in enumerate(titles):
        data = df[title].value_counts().head(4)

        labels = data.index
        sizes = data.values

        fig, ax = plt.subplots()
        ax.pie(sizes, autopct='%1.1f%%', startangle=30, textprops={'color': 'white', 'fontsize': 13})
        ax.axis('equal')

        legend = ax.legend(labels, title=f"{title}", loc="lower left", fontsize=11, bbox_to_anchor=(0.62, 0))

        img_buffer = BytesIO()
        #plt.title(f"{title} Distribution", color='white', fontsize=16)
        plt.savefig(img_buffer, format='png', transparent=True)

        img_buffer.seek(0)
        plt.close()

        pie_data.append(base64.b64encode(img_buffer.getvalue()).decode('utf-8'))
        pie_data_titles.append(f"{title} Distribution")

    return pie_data, pie_data_titles

def generate_pie_chart(data_list):
    img_data_base64 = []

    for i, data in enumerate(data_list):
        img_data_base64.append(data)

    return img_data_base64

def create_time_series_plots(df):
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    unique_log_names = df['LogName'].unique()
    plot_divs = []
    plot_divs_titles = []

    for log_name in unique_log_names:
        subset_df = df[df['LogName'] == log_name]

        log_count_by_time = subset_df.groupby('Datetime').size().reset_index(name='LogCount')

        trace = go.Scatter(x=log_count_by_time['Datetime'], y=log_count_by_time['LogCount'])
        layout = go.Layout(
            xaxis=dict(title='Datetime'),
            yaxis=dict(title='LogCount'),
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            autosize=False,
            width=400,
            height=300
        )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = fig.to_html(full_html=False)
        plot_divs.append(plot_div)
        plot_divs_titles.append(f'{log_name} Logs Count over Time')

    return plot_divs, plot_divs_titles