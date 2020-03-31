import pandas as pd
import geopandas as gpd
import plotly.graph_objs as go


def df_prepare(dataset, pop_dataset=None, historical=False, continent=None, top_n = None):
    """Clean world bank data for a visualizaiton dashboard

    Keeps data range of dates in keep_columns variable and data for the top 10 economies
    Reorients the columns into a year, country and value
    Saves the results to a csv file

    Args:
        dataset (str): path of the csv data file

    Returns:
        clean data (dataframe)

    """
    # read datasets

    df = pd.read_csv(dataset) #

    if pop_dataset:

        df_pop = pd.read_csv(pop_dataset, delimiter=";") # population dataset


    # clean data

    df = df.rename(columns={"ObservationDate": "Date", "Country/Region": "Country"})

    df = df.groupby(['Country', 'Date']).sum().reset_index()


    df['Country'] = df['Country'].replace({'UK': 'United Kingdom',
                                           'US': 'United States',
                                           'Mainland China': 'China',
                                           'Czech Republic': 'Czechia',
                                           })



    if pop_dataset:

        df = df.set_index('Country').join(df_pop.set_index('Country'))
        df.dropna(subset=['Population'], inplace=True)

        df['Infected'] = df['Confirmed'] - df['Recovered'] - df['Deaths']

        df['Confirmed_percent'] = 100*df['Confirmed']/(df['Population'] + 1.0)
        df['Recovered_percent'] = 100*df['Recovered']/(df['Population'] + 1.0)
        df['Deaths_percent'] = 100*df['Deaths']/(df['Population'] + 1.0)
        df['Infected_percent'] = 100*df['Infected']/(df['Population'] + 1.0)

        df['Confirmed_per_100k'] = 100000*df['Confirmed']/(df['Population'] + 1.0)
        df['Recovered_per_100k'] = 100000*df['Recovered']/(df['Population'] + 1.0)
        df['Deaths_per_100k'] = 100000*df['Deaths']/(df['Population'] + 1.0)
        df['Infected_per_100k'] = 100000*df['Infected']/(df['Population'] + 1.0)

    # filter/select data based on continent, selected_countries and historical

        if continent:
            df = df[df['Continent'] == continent]

    #df = df.loc[df.index.isin(selected_countries), :]

    df = df.reset_index().set_index('Date')
    df.index = pd.to_datetime(df.index, infer_datetime_format=True)

    if historical:

        df = df.query("index >= '2020-03-08'")
        df = df[['Continent', 'Country', 'Population', 'Infected', 'Recovered', 'Deaths',
                 'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                 'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

    else:

        df = df[df.index == df.index.max()]
        if pop_dataset:
            df = df[['Continent', 'Country', 'Short', 'Population', 'Infected', 'Recovered', 'Deaths',
                     'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                     'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

            df = df.reset_index().set_index('Country')
        else:
            df = df[['Continent', 'Country', 'Population', 'Infected', 'Recovered', 'Deaths',
                     'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                     'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

            df = df.reset_index().set_index('Country')


    return df

def prepare_geo():

    fp = 'web_app/data/ne_10m_admin_0_countries.shp'

    gdf = gpd.read_file(fp)

    gdf = gdf.rename(columns={"ADMIN": "Country", "ADM0_A3": "Short"})

    gdf = gdf[['Country', 'Short', 'geometry']]


    df_all = df_prepare('web_app/data/covid_19_data.csv', 'web_app/data/population_2020_for_johnhopkins_data.csv',
                    historical = False,
                    continent = None)

    df = gdf.merge(df_all, how='left', on='Short').drop(columns=['Date'])

    return df


def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

  # first chart plots arable land from 1990 to 2015 in top 10 economies
  # as a line chart

    graph_one = []
    df = prepare_geo()
    df = df[['Country', 'Short', 'Infected_per_100k']]
    df.sort_values('Infected_per_100k', ascending=False, inplace=True)

    graph_one.append(
        go.Choropleth(
            locations = df['Short'],
            z = df['Infected_per_100k'],
            text = df['Country'],
            colorscale = 'Blues',
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Infected<br>per 100,000',
            )
        )

    layout_one = dict(
        title = 'Global Infected per 100,000 people',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
            )
        )



    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))

    return figures
