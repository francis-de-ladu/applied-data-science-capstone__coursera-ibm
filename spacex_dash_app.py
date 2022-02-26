# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import requests
import os


# download dataset if file doesn't exist
dataset_fn = "spacex_launch_dash.csv"
if not os.path.isfile(dataset_fn):
    dataset_url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
    response = requests.get(dataset_url, allow_redirects=True)
    with open(dataset_fn, 'wb+') as file:
        file.write(response.content)


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=
            [{'label': 'All Sites', 'value': 'ALL'}] + \
                [{'label': launch_site, 'value': launch_site}
                 for launch_site in sorted(
                     spacex_df['Launch Site'].value_counts().keys()
                )],
        placeholder='Select a Launch Site here',
        searchable=True,
    ),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks = {str(x): str(x) for x in np.linspace(0, 10000, 5, dtype=np.int32)},
        value=[min_payload, max_payload],
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            data,
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site',
        )
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = filtered_df['class'].value_counts().reset_index()
        fig = px.pie(
            data,
            values='class', 
            names='index', 
            title=f'Total Success Launches for site {entered_site}',
        )

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value'),
)
def get_scatter_chart(entered_site, payload_range):
    min_payload, max_payload = payload_range
    mask1 = spacex_df['Payload Mass (kg)'] > min_payload
    mask2 = spacex_df['Payload Mass (kg)'] <= max_payload
    filtered_df = spacex_df[mask1 & mask2]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class', 
            title='Correlation between Payload and Success for all Sites',
            color="Booster Version Category",
        )
    else:
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class', 
            title=f'Correlation between Payload and Success for site {entered_site}',
            color="Booster Version Category",
        )

    return fig



# Run the app
if __name__ == '__main__':
    app.run_server()
