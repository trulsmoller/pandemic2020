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

        df = df.query("index >= '2020-04-05'")
        df = df[['Continent', 'Country', 'Population', 'Confirmed', 'Infected', 'Recovered', 'Deaths',
                 'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                 'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

    else:

        df = df[df.index == df.index.max()]
        if pop_dataset:
            df = df[['Continent', 'Country', 'Short', 'Population', 'Confirmed', 'Infected', 'Recovered', 'Deaths',
                     'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                     'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

            df = df.reset_index().set_index('Country')
        else:
            df = df[['Continent', 'Country', 'Population', 'Confirmed', 'Infected', 'Recovered', 'Deaths',
                     'Infected_percent', 'Recovered_percent', 'Deaths_percent',
                     'Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']]

            df = df.reset_index().set_index('Country')


    return df

def prepare_geo():

    fp = 'data/ne_10m_admin_0_countries.shp'

    gdf = gpd.read_file(fp)

    gdf = gdf.rename(columns={"ADMIN": "Country", "ADM0_A3": "Short"})

    gdf = gdf[['Country', 'Short', 'geometry']]


    df_all = df_prepare('data/covid_19_data.csv', 'data/population_2020_for_johnhopkins_data.csv',
                    historical = False,
                    continent = None)

    df = gdf.merge(df_all, how='left', on='Short').drop(columns=['Date'])

    return df


def prepare_bar(var, continent = None, top_n = None):

    var_list_abs = ['Infected', 'Recovered', 'Deaths']
    var_list_rel1 = ['Infected_percent', 'Recovered_percent', 'Deaths_percent']
    var_list_rel2 = ['Infected_per_100k', 'Recovered_per_100k', 'Deaths_per_100k']

    continent_list = ['America', 'Europe', 'Asia', 'Africa', 'Oceania']

    if continent:
        assert continent in continent_list


    keyword1 = '_percent'
    keyword2 = '_per_100k'

    if keyword1 in var:

        stat = '(relative to population)'
        var_list = var_list_rel1

    elif keyword2 in var:

        stat = '(relative to population)'
        var_list = var_list_rel2

    else:
        stat = ''
        var_list = var_list_abs


    df = df_prepare('data/covid_19_data.csv', 'data/population_2020_for_johnhopkins_data.csv',
                    historical = False,
                    continent = continent)

    if top_n:
        tot_countries = df.shape[0]
        if top_n > tot_countries:
            top_n = tot_countries

    if not continent:
        continent = "The World"

    df = df.sort_values(by=[var], ascending=False).loc[:, var_list][:top_n].reset_index()
    df = df.sort_values(by=[var], ascending=True)
    return df

def prepare_time(var, continent=None, top_n = None):


    df = df_prepare('data/covid_19_data.csv', 'data/population_2020_for_johnhopkins_data.csv',
                    historical = True,
                    continent = continent)

    # steps to add new metrics such as death rate

    countries = df.Country.unique()

    for i, country in enumerate(countries):

        days_delay = 6

        if i == 0:


            df1 = df.loc[df['Country'] == country]
            df1['Conf_n_daysago'] = df1['Confirmed'].shift(days_delay)
            df1['Mortality_rate'] = 100*df1['Deaths'] / (df1['Conf_n_daysago'] + 0.00001)
            #df1['Recovered_in_n_days'] = df1['Deaths']*(1/(df1['Mortality_rate']/100 + 0.0000001) - 1)

        elif i > 0:

            df_single = df.loc[df['Country'] == country]
            df_single['Conf_n_daysago'] = df_single['Confirmed'].shift(days_delay)
            df_single['Mortality_rate'] = 100*df_single['Deaths'] / (df_single['Conf_n_daysago'] + 0.00001)
            #df_single['Recovered_in_n_days'] = df_single['Deaths']*(1/(df_single['Mortality_rate']/100 + 0.0000001) - 1)

            frames = [df1, df_single]
            df1 = pd.concat(frames)

    df = df1


    # initializing the plot of df
    dic = dict()

    y = var
    group = 'Country'

    tot_countries = df.shape[0]

    if top_n:
        if top_n > tot_countries:
            top_n = tot_countries
    else:
        top_n = tot_countries


    last_date = df.index.max()

    df_last = df[df.index == last_date].sort_values(var, ascending=False)
    countrylist = list(df_last[group][:top_n])

    df = df.reset_index()



    return countrylist, df


def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

  # first chart plots arable land from 1990 to 2015 in top 10 economies
  # as a line chart

    graph_zero = []
    df = prepare_geo()
    df = df[['Country', 'Short', 'Infected_percent']]
    df.sort_values('Infected_percent', ascending=False, inplace=True)

    graph_zero.append(
        go.Choropleth(
            locations = df['Short'],
            z = df['Infected_percent'],
            text = df['Country'],
            colorscale = 'Viridis_r',
            #Viridis_r
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Infected',
            colorbar_ticksuffix = '%',
            )
        )

    layout_zero = dict(
        title = 'All Countries: Percent of Population Currently Infected (registrered)',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
            )
        )

    graph_one = []
    df = prepare_geo()
    df = df[['Country', 'Short', 'Recovered_percent']]
    df.sort_values('Recovered_percent', ascending=False, inplace=True)

    graph_one.append(
        go.Choropleth(
            locations = df['Short'],
            z = df['Recovered_percent'],
            text = df['Country'],
            colorscale = 'Viridis_r',
            #Viridis_r
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Recovered',
            colorbar_ticksuffix = '%',
            )
        )

    layout_one = dict(
        title = 'All Countries: Percent of Population Currently Recovered (registrered)',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
            )
        )


    graph_two = []
    df = prepare_geo()
    df = df[['Country', 'Short', 'Deaths_per_100k']]
    df.sort_values('Deaths_per_100k', ascending=False, inplace=True)

    graph_two.append(
        go.Choropleth(
            locations = df['Short'],
            z = df['Deaths_per_100k'],
            text = df['Country'],
            colorscale = 'Viridis_r',
            #Viridis_r
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Deaths/ 100k',
            colorbar_ticksuffix = '',
            )
        )

    layout_two = dict(
        title = 'All Countries: Deaths per 100,000 People',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
            )
        )





    graph_three = []
    countrylist, df = prepare_time('Infected_percent', continent = '', top_n = 15)

    df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Infected_percent.tolist()
      graph_three.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_three = dict(title = 'Percent of Population Infected',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Infected in percent'),
                xaxis_rangeslider_visible=True)

    graph_four = []
    countrylist, df = prepare_time('Recovered_percent', continent = '', top_n = 15)

    df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Recovered_percent.tolist()
      graph_four.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_four = dict(title = 'Percent of Population Recovered',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Recovered in percent'),
                xaxis_rangeslider_visible=True)


    graph_five = []
    countrylist, df = prepare_time('Deaths_per_100k', continent = '', top_n = 15)

    df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Deaths_per_100k.tolist()
      graph_five.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_five = dict(title = 'Deaths per 100,000',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Deaths'),
                xaxis_rangeslider_visible=True)


    graph_six = []
    countrylist, df = prepare_time('Mortality_rate', continent = 'Europe', top_n = 15)

    df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Mortality_rate.tolist()
      graph_six.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_six = dict(title = 'Mortality Rates Europe (work-in-progress)',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Percent'),
                xaxis_rangeslider_visible=True)


    graph_seven = []
    df = prepare_bar('Deaths_per_100k', continent = 'America', top_n = 10)
    df = df.sort_values('Deaths_per_100k', ascending=False)

    graph_seven.append(
      go.Bar(
      y = df.Deaths_per_100k.tolist(),
      x = df.Country.tolist(),
      #orientation = 'h',
      )
    )

    layout_seven = dict(title = 'America Ranked by Deaths per 100,000 People',
                yaxis = dict(title = 'Deaths per 100k'),
                xaxis = dict(title = ''),
                )

    graph_eight = []
    df = prepare_bar('Deaths_per_100k', continent = 'Europe', top_n = 25)
    df = df.sort_values('Deaths_per_100k', ascending=False)

    graph_eight.append(
      go.Bar(
      y = df.Deaths_per_100k.tolist(),
      x = df.Country.tolist(),
      #orientation = 'h',
      )
    )

    layout_eight = dict(title = 'Europe Ranked by Deaths per 100,000 People',
                yaxis = dict(title = 'Deaths per 100k'),
                xaxis = dict(title = ''),
                )


    graph_nine = []
    df = prepare_bar('Deaths_per_100k', continent = 'Asia', top_n = 20)
    df = df.sort_values('Deaths_per_100k', ascending=False)

    graph_nine.append(
      go.Bar(
      y = df.Deaths_per_100k.tolist(),
      x = df.Country.tolist(),
      #orientation = 'h',
      )
    )

    layout_nine = dict(title = 'Asia Ranked by Deaths per 100,000 People',
                yaxis = dict(title = 'Deaths per 100k'),
                xaxis = dict(title = ''),
                )

    graph_ten = []
    df = prepare_bar('Deaths_per_100k', continent = 'Africa', top_n = 10)
    df = df.sort_values('Deaths_per_100k', ascending=False)

    graph_ten.append(
      go.Bar(
      y = df.Deaths_per_100k.tolist(),
      x = df.Country.tolist(),
      #orientation = 'h',
      )
    )

    layout_ten = dict(title = 'Africa Ranked by Deaths per 100,000 People',
                yaxis = dict(title = 'Deaths per 100k'),
                xaxis = dict(title = ''),
                )

    graph_eleven = []
    df = prepare_bar('Deaths_per_100k', continent = 'Oceania', top_n = 3)
    df = df.sort_values('Deaths_per_100k', ascending=False)

    graph_eleven.append(
      go.Bar(
      y = df.Deaths_per_100k.tolist(),
      x = df.Country.tolist(),
      #orientation = 'h',
      )
    )

    layout_eleven = dict(title = 'Oceania Ranked by Deaths per 100,000 People',
                yaxis = dict(title = 'Deaths per 100k'),
                xaxis = dict(title = ''),
                )

#    table_one = []
#    df = prepare_bar('Deaths_per_100k', continent = 'Africa', top_n = 10)
#    df = df.sort_values('Deaths_per_100k', ascending=False)
#    df = df[['Short', 'Deaths_per_100k']]
#    fig = go.Figure(data=[go.Table(
#    header=dict(values=list(df.columns),
#                fill_color='paleturquoise',
#                align='left'),
#    cells=dict(values=[df.Short, df.Deaths_per_100k],
#               fill_color='lavender',
#               align='left'))
#
#    ])

    #table_one.append(
#        fig
#    )

    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_zero, layout=layout_zero))
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))
    figures.append(dict(data=graph_six, layout=layout_six))
    figures.append(dict(data=graph_seven, layout=layout_seven))
    figures.append(dict(data=graph_eight, layout=layout_eight))
    figures.append(dict(data=graph_nine, layout=layout_nine))
    figures.append(dict(data=graph_ten, layout=layout_ten))
    figures.append(dict(data=graph_eleven, layout=layout_eleven))
    #figures.append(dict(data=table_one))

    return figures
