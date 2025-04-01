import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

data = {
    "Team": [
        "Brazil", "Germany", "Italy", "Argentina", "France", "Uruguay",
        "England", "Spain", "Netherlands", "Hungary", "Czechoslovakia",
        "Sweden", "Croatia"
    ],
    "Winners": [5, 4, 4, 3, 2, 2, 1, 1, 0, 0, 0, 0, 0],
    "RunnersUp": [2, 4, 2, 3, 2, 0, 0, 0, 3, 2, 2, 1, 1],
    "YearsWon": [
        "1958, 1962, 1970, 1994, 2002",
        "1954, 1974, 1990, 2014",
        "1934, 1938, 1982, 2006",
        "1978, 1986, 2022",
        "1998, 2018",
        "1930, 1950",
        "",
        "2010",
        "",
        "",
        "",
        "",
        ""
    ],
    "YearsRunnersUp": [
        "1950, 1998",
        "1966, 1982, 1986, 2002",
        "1970, 1994",
        "1930, 1990, 2014",
        "2006, 2022",
        "",
        "1966",
        "",
        "1974, 1978, 2010",
        "1938, 1954",
        "1934, 1962",
        "1958",
        "2018"
    ]
}

df = pd.DataFrame(data)

country_iso_map = {
    "Brazil": "BRA", "Germany": "DEU", "Italy": "ITA", "Argentina": "ARG",
    "France": "FRA", "Uruguay": "URY", "England": "GBR", "Spain": "ESP",
    "Netherlands": "NLD", "Hungary": "HUN", "Czechoslovakia": "CZE",
    "Sweden": "SWE", "Croatia": "HRV"
}
df["ISO"] = df["Team"].map(country_iso_map)

year_set = set()
for col in ["YearsWon", "YearsRunnersUp"]:
    for years in df[col]:
        if pd.notna(years):
            for year in str(years).split(','):
                year = year.strip()
                if year.isdigit():
                    year_set.add(int(year))
sorted_years = sorted(list(year_set))

app = dash.Dash(__name__)
app.title = "FIFA World Cup Dashboard"
server = app.server 

app.layout = html.Div([
    html.H1("FIFA World Cup Winners & Runner-Ups"),

    html.Label("Select a Country:"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{"label": c, "value": c} for c in df["Team"]],
        placeholder="Select a country"
    ),
    html.Div(id='country-output', style={'marginBottom': '20px'}),

    html.Label("Select a Year:"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{"label": y, "value": y} for y in sorted_years],
        placeholder="Select a year"
    ),
    html.Div(id='year-output', style={'marginBottom': '20px'}),

    dcc.Graph(id='choropleth-map')
])

@app.callback(
    Output('country-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_output(selected_country):
    if not selected_country:
        return "Please select a country."
    selected_country = selected_country.strip()
    if selected_country in df["Team"].values:
        wins = df[df["Team"] == selected_country]["Winners"].values[0]
        return f"{selected_country} has won the FIFA World Cup {wins} times."
    return f"{selected_country} is not in the data."

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_map(selected_year, selected_country):
    df_copy = df.copy()

    if selected_year:
        df_copy["Result"] = "None"
        winner = runner_up = None

        for _, row in df.iterrows():
            if str(selected_year) in str(row["YearsWon"]):
                winner = row["Team"]
                df_copy.loc[df_copy["Team"] == winner, "Result"] = "Winner"
            if str(selected_year) in str(row["YearsRunnersUp"]):
                runner_up = row["Team"]
                df_copy.loc[df_copy["Team"] == runner_up, "Result"] = "Runner-up"

        fig = px.choropleth(
            df_copy,
            locations="ISO",
            color="Result",
            hover_name="Team",
            color_discrete_map={
                "Winner": "green",
                "Runner-up": "orange",
                "None": "lightgray"
            },
            title=f"World Cup Result in {selected_year}"
        )
        return fig

    elif selected_country:
        selected_country = selected_country.strip()
        selected_row = df[df["Team"] == selected_country]
        fig = px.choropleth(
            selected_row,
            locations="ISO",
            color="Winners",
            hover_name="Team",
            hover_data={"Winners": True},
            color_continuous_scale="Viridis",
            range_color=(1, df["Winners"].max()),
            title=f"{selected_country} World Cup Performance"
        )
        fig.update_geos(visible=False, resolution=50, showcountries=True, fitbounds="locations")
        return fig

    else:
        fig = px.choropleth(
            df,
            locations="ISO",
            color="Winners",
            hover_name="Team",
            color_continuous_scale="Viridis",
            range_color=(1, df["Winners"].max()),
            title="Countries that have won the FIFA World Cup"
        )
        return fig

if __name__ == '__main__':
    app.run_server(debug=True)
