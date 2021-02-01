# import json
# import pandas as pd
# import plotly
import plotly.express as px  
import plotly.graph_objects as go
# import plotly.io as pio
from plotly.subplots import make_subplots

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from data_handling import prepare_dataframe, prepare_json, calc_proportion_WPP, calc_proportion_WWP, bar_data

# Inputs
data_dir = r"data"
json_file = r"Polska.geojson"


# Init the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 

pl_json = prepare_json(json_file)
data = prepare_dataframe(data_dir)
data_bar = prepare_dataframe(data_dir)
bar_df = bar_data(data_bar)
years = {"Rok": [str(i) for i in range(2004, 2020)]}

###################################
barchart = px.bar(data_frame=bar_df,
                      x="Województwo",
                      y="Deaths",
                      color="Sex",
                      orientation="v",
                      barmode="group",
                      animation_frame="Year",
                      range_y=[0, 1100],
                      category_orders=years,
                      labels={"Województwo": " "},
                      # title="ABC"
                      )
barchart.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
barchart.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
barchart.update_layout(title={
        'text': "Deaths of male and female in 80 years old",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

###################################

def annotate():
    annotations = []
    ann_data = [(0.385, 0.775, "Zachodniopomorskie", "https://szczecin.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.46, 0.83, "Pomorskie"         , "https://gdansk.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.555, 0.81, "Warmińsko-Mazurskie", "https://olsztyn.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.615, 0.71, "Podlaskie"          , "https://bialystok.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.375, 0.575, "Lubuskie"          , "https://zielonagora.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.44, 0.55, "Wielkopolskie"      , "https://poznan.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.48, 0.70, "Kujawsko-Pomorskie" , "https://bydgoszcz.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.565, 0.59, "Mazowieckie"        , "https://warszawa.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.41, 0.375, "Dolnosląśkie"       , "https://wroclaw.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.51, 0.45, "Łódzkie"            , "https://lodz.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.56, 0.355, "Świętokrzyskie"     , "https://kielce.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.615, 0.43, "Lubelskie"          , "https://lublin.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.465, 0.32, "Opolskie"           , "https://opole.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.50, 0.30, "Śląskie"            , "https://katowice.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.54, 0.22, "Małopolskie"        , "https://krakow.stat.gov.pl/dane-o-wojewodztwie/"),
                (0.605, 0.24, "Podkarpackie"       , "https://rzeszow.stat.gov.pl/dane-o-wojewodztwie/")]

    for ann in ann_data:
        ann_dict = {"x": ann[0],
                    "y": ann[1],
                    "xref": "paper",
                    "yref": "paper",
                    "text": f'<a href="{ann[3]}">{ann[2]}</a>',
                    "font": dict(color="#ff7f0e", size=9),        
                    "showarrow": False}
        
        annotations.append(ann_dict)
        
    return annotations


def bar_subplots(df, column, mode):
    dff = df.copy()
    wojewodztwa = ("Zachodniopomorskie", "Pomorskie", "Warmińsko-Mazurskie", "Podlaskie",
                        "Lubuskie", "Wielkopolskie", "Kujawsko-Pomorskie", "Mazowieckie",
                        "Dolnośląskie", "Łódzkie", "Świętokrzyskie", "Lubelskie",
                        "Opolskie", "Śląskie", "Małopolskie", "Podkarpackie")
    
    if mode == "WWP":
        fig = make_subplots(rows=4, cols=4, subplot_titles=wojewodztwa)
        
        if column.split("-")[0] == "MĘ":
            sex = ["Male"]
            dff = dff[["Województwo", column]]
        elif column.split("-")[0] == "KO":
            sex = ["Female"]
            dff = dff[["Województwo", column]]


        max_deaths = max(dff[column])
            
        row, col = 1, 1
        for woj in wojewodztwa:    
            deaths = [int(dff.query(f"Województwo=='{woj}'")[column])]

            fig.add_trace(go.Bar(x=sex, y=deaths, width=0.1, marker_color='indianred'), row=row, col=col)
            fig.update_yaxes(range=[0, 1.1*max_deaths], row=row, col=col)
            
            if col == 4:
                col = 0
                row += 1
                
            col += 1
            
        fig.update_layout(height=700, width=1500, showlegend=False)
            
            
    elif mode == "WPP":
        spec = [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}, {"type": "domain"}]
        specs = [spec, spec, spec, spec]
        fig = make_subplots(rows=4, cols=4, subplot_titles=wojewodztwa, specs=specs)
        
        print(column)
        sex = ["Female", "Male"]
        
        if column.split("-")[0] == "MĘ":
            male_column   = column
            female_column = column.replace("MĘ", "KO")
            
        elif column.split("-")[0] == "KO":
            male_column   = column.replace("KO", "MĘ")
            female_column = column
            
        dff = dff[["Województwo", female_column, male_column]]

        # max_deaths = max([max(dff[male_column]), max(dff[female_column])])
            
        row, col = 1, 1
        for woj in wojewodztwa:  
            female_deaths = int(dff.query(f"Województwo=='{woj}'")[female_column])
            male_deaths   = int(dff.query(f"Województwo=='{woj}'")[male_column])
            deaths = [female_deaths, male_deaths]

            fig.add_trace(go.Pie(labels=sex, values=deaths), row=row, col=col)
        
            if col == 4:
                col = 0
                row += 1
                
            col += 1
           
        fig.update_layout(height=700, width=1500)


    return fig

###################################

old_list  = [{"label": str(i), "value": i} if i < 110 else {"label": "110 and more", "value": i} for i in range(111)]
year_list = [{"label": str(i), "value": i} for i in data.keys()]

# Make a layout
app.layout = html.Div([

    html.H1("Deaths in Poland over the years", style={'text-align': 'center'}),
    
    html.Div(dcc.Markdown('''This interactive visualization was created to obtain some information about deaths in Poland in the years 2004-2019. The project is aimed at people who want to get detailed and in-depth knowledge about the occurance and formations of deaths in individual Voivodeship. The user can select the details, on which he/she wishes to obtain information, by selecting the appropriate values ​​in the fields below. Data visualization is possible by selecting: **year** (2004-2019), **gender** (Female, Male), **age** (0-110) and the **mode** in which the map and graphs will be presented. If the user would like to get more information on deaths, population or other statistical information about a given Voivodeship, he/she can be redirected to the website of the Statistical Office in the given Voivodeship, after clicking on the name of this Voivodeship. This analytical dashboard allows the user to make in-depth analysis of the topic and to formulate conclusions (maybe even forecasts) resulting from the information that may be visualized below.''')),
    
    html.Div([html.Div(dcc.Dropdown(id="slct_year",
                  options=year_list,
                  multi=False,
                  value=2015,
                  ), style={'width': "10%",'marginTop': 65, "margin-left": "55px", 'display': 'inline-block'}),
    
    html.Div(dcc.Dropdown(id="slct_gender",
                  options=[
                      {"label": "Female",   "value": "KO"},
                      {"label": "Male", "value": "MĘ"}],
                  multi=False,
                  value="MĘ",
                  ), style={'width': "10%", "margin-left": "55px", 'display': 'inline-block'}),
    
    html.Div(dcc.Dropdown(id="slct_old",
                  options=old_list,
                  multi=False,
                  value="80"),
                  style={'width': "10%", "margin-left": "55px", 'display': 'inline-block'})
            ]),
    
    html.Div(html.Button(id="visualize_button",
                  children="Submit",
                  n_clicks=0),
                  style={'width': "15%", "margin-left": "670px", "marginTop":-44}),

     html.Div(dcc.RadioItems(id="slct_option",
                  options=[{"label": "Regarding choosen sex",   "value": "WWP"},
                           {"label": "Regarding opposite sex", "value": "WPP"}],
                  value="WWP",
                  labelStyle={'display': 'inline-block'}), 
                  style={"margin-left": "1050px", "marginTop":-30}),
     
     html.Div(dcc.Markdown("""
                           Mode:
                           """), 
                  style={"margin-left": "1000px", "marginTop":-50}), #1110
    
    html.Br(),

    html.Div(dcc.Graph(id='my_bee_map', figure={}),
             style={"marginTop":10}),
    
    html.Br(),
    
    
    # html.Div(dcc.Graph(figure=fig)),
    html.Div(dcc.Graph(id='bar_charts', figure={})),
    
    html.Br(),
    
    
    html.Div(dcc.Graph(figure=barchart)),
    
    html.Br(),
    
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback([Output(component_id='my_bee_map',     component_property='figure'),
               Output(component_id='bar_charts',     component_property='figure')],
              [Input(component_id="visualize_button", component_property="n_clicks")],
    [State(component_id='slct_year',   component_property='value'),
     State(component_id='slct_gender', component_property='value'),
     State(component_id='slct_old',    component_property='value'),
     State(component_id='slct_option', component_property='value')])
def update_graph(n_clicks, slct_year, slct_gender, slct_old, slct_option):
    if slct_old == 110:
        color = f"{slct_gender}-{slct_old}+-{slct_year}"
    else:
        color = f"{slct_gender}-{slct_old}-{slct_year}"
        
    df = data[str(slct_year)]
    dff = df.copy()
    dff.drop(df.index[0], inplace=True)
    
    if slct_option == "WWP":
        ccs = px.colors.sequential.Oranges   
        data_WWP = calc_proportion_WWP(dff, color)
        fig = px.choropleth(data_WWP,
                            locations="Województwo",
                            geojson=pl_json,
                            color="Ratio",
                            color_continuous_scale=ccs,
                            scope="europe")
        
        bar_figure = bar_subplots(dff, color, mode="WWP")
        
    elif slct_option == "WPP":
        bar_figure = bar_subplots(dff, color, mode="WPP")
        
        if slct_gender == "MĘ" or slct_gender == "KO":
            if slct_old == 110:
                clmn = f"OG-{slct_old}+-{slct_year}"
            else:
                clmn = f"OG-{slct_old}-{slct_year}"
                
        ccs = px.colors.sequential.speed
        data_WPP = calc_proportion_WPP(dff, clmn, color)
        data_WPP_copy = data_WPP.copy()
        fig = px.choropleth(data_WPP_copy,
                            locations="Województwo",
                            geojson=pl_json,
                            color="Ratio",
                            color_continuous_scale=ccs,
                            scope="europe")
        
        
            
    ann = annotate()
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, annotations=ann, dragmode=False)
    
    # --------------------------
    
    
    return fig, bar_figure 

if __name__ == '__main__':
    app.run_server(debug=True)