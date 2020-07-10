import pandas as pd
import numpy as np
import datetime as dt
import plotly.graph_objs as go


def get_popdata(popdata_path):
    '''
    This function reads the population data from csv file into a pandas DataFrame, cleans up the
    column names and transforms 'Urban population ratio' data to type Float.

    The data contains the following on country-level:

    - Country name
    - ISO code as described in the ISO 3166 international standard, the 3-letter version ('Short')
    - Continent
    - Population
    - Population per square kilometer
    - Median age
    - Urban population ratio

    Args
        popdata_path (str): path to the population data file

    Returns:
        df_pop (dataframe): population dataframe
    '''

    # population dataset read into dataframe
    df_pop = pd.read_csv(popdata_path, delimiter=";")

    # setting column headers
    df_pop.columns = ['Country', 'ISO', 'Continent', 'Population', 'Pop_km2', 'Median_age', 'Urban_Population_percent']

    # extracting the ratio from string column 'UrbanPopPercent' and replacing it with a new column with
    # float values for ratio.
    df_pop['Urban_Population_ratio'] = df_pop['Urban_Population_percent'].str.strip('%').astype(float).div(100)
    df_pop.drop('Urban_Population_percent', axis = 1, inplace=True)

    return df_pop

def get_covid_data(data_path):
    '''
    This function reads the covid-19 data from csv file into a pandas DataFrame, cleans up the
    column names and updates some of the country names to match the ones used in the population dataset.

    The data contains the following on country-level:
    - Country name
    - Date (Daily. The start date is not the same for all countries; it ranges from January to March 2020)
    - Deaths (total number for respective country at respective date)

    Args:
        data_path (str): path to covid-19 data file

    Returns:
        this function does not return anything
    '''

    df = pd.read_csv(data_path) # population dataset read into dataframe

    # clean data

    df = df.rename(columns={"ObservationDate": "Date", "Country/Region": "Country"})

    df = df.groupby(['Country', 'Date']).sum().reset_index()

    # update some of the country names to match the ones used in the population dataset

    df['Country'] = df['Country'].replace({'UK': 'United Kingdom',
                                           'US': 'United States',
                                           'Mainland China': 'China',
                                           'Czech Republic': 'Czechia',
                                           'Burma': 'Myanmar'
                                           })
    try:
        df['Country'] = df['Country'].replace({"('St. Martin',)": "St. Martin",
                                               "occupied Palestinian territory": "Palestine",
                                               "State of Palestine": "Palestine",
                                               "Ivory Coast": "Cote d'Ivoire",
                                               "Gambia, The": "Gambia",
                                               "The Gambia": "Gambia",
                                               "The Bahamas": "Bahamas",
                                               "Bahamas, The": "Bahamas",
                                               "Republic of Ireland": "Ireland",
                                               "Republic of the Congo": "Congo (Brazzaville)",
                                               " Azerbaijan": "Azerbaijan"

                                              })
    except:
        pass

    # sort on Country, then Date. Mostly it is only one row getting grouped, whereever data is on regional
    # groupby ensures we get the data summed up to country level
    df_covid = df.groupby(['Country', 'Date']).sum().reset_index()

    # dropping columns we will not use.
    df_covid.drop(['SNo', 'Confirmed', 'Recovered'], axis=1, inplace=True)

    df_covid.columns = ['Country', 'Date', 'Total_deaths']

    return df_covid


def merge_data():
    '''
    This function get the population data and the covid-19 data and merges it to one dataframe

    Args:
        None

    Returns:
        df_merged (dataframe): merged data
    '''

    popdata_path = 'data/population_2020_for_johnhopkins_data.csv'
    data_path = 'data/covid_19_data.csv'

    df_pop = get_popdata(popdata_path)

    df_covid = get_covid_data(data_path)

    df_merged = df_covid.set_index('Country').join(df_pop.set_index('Country')).reset_index()

    df_merged.dropna(subset=['Population'], inplace=True)



    df_merged = df_merged[['Date', 'Continent', 'Country', 'ISO', 'Population', 'Urban_Population_ratio', 'Pop_km2', 'Median_age', 'Total_deaths']]

    df_merged.Date = pd.to_datetime(df_merged.Date, infer_datetime_format=True)

    return df_merged

def add_calculated_cols(df_merged):
    '''
    This function adds some calculated columns to the dataframe

    Args:
        df_merged (dataframe): df containing covid-19 data as well as population data

    Returns:
        df_full (dataframe): With new calculated columns added
    '''
    df = df_merged.copy()

    df['Total_deaths_per_100k'] = 100000*df['Total_deaths']/(df['Population'] + 1.0)

    df['Weekday'] = df['Date'].dt.weekday

    df['Year_week'] = df['Date'].dt.strftime('%G-%V')

    country_codes = df.ISO.unique().tolist()

    country_dfs = []

    for code in country_codes:

        notgrouped = df[df['ISO'] == code]
        notgrouped.set_index('Year_week')
        notgrouped['Total_deaths_yesterday'] = notgrouped['Total_deaths'].shift(1).fillna(0)
        notgrouped['Deaths'] = notgrouped['Total_deaths'] - notgrouped['Total_deaths_yesterday']
        notgrouped.drop(['Total_deaths_yesterday'], axis=1, inplace=True)
        notgrouped.set_index('Year_week', inplace=True)

        grouped = notgrouped.groupby(['Year_week']).sum()
        grouped.rename(columns={"Deaths": "Deaths_week"}, inplace=True)
        grouped['Deaths_lastweek'] = grouped['Deaths_week'].shift(1).fillna(0)
        grouped['Infection_rate'] =  (grouped['Deaths_week'] / grouped['Deaths_lastweek']).fillna(0).replace(np.inf, 0)
        grouped = grouped[['Deaths_week', 'Deaths_lastweek', 'Infection_rate']]

        regrouped = notgrouped.join(grouped)

        #regrouped.rename(columns={"Deaths": "Deaths_week"}, inplace=True)

        country_dfs.append(regrouped)

    df_full = pd.concat(country_dfs)

    df_full['Deaths_per_100k'] = 100000*df_full['Deaths']/(df_full['Population'] + 1.0)

    df_full.reset_index(inplace=True)

    return df_full


def dates_choice(df, all_dates=False, weekly=False):
    '''
    This function selects dates based on input. There are three types

    1. Historic daily data (all_dates=True)
    2. Historic weekly data (weekly=True, all_dates=False)
    2. Latest date data (weekly=False, all_dates=False)

    The historic data will be suitable for performing time series analysis.

    The latest date data will be suitable to look at the overall picture (such as accumulated death
    count per country).

    Args:
        df (dataframe): df containing covid-19 data as well as population data

        all_dates (boolean): Optional argument - True if you wish to get daily historic data

        weekly (boolean): Optional argument - True if you wish to get historic weekly data

    Returns:
        df (dataframe): Based on choices
    '''

    if all_dates:

        # No filtering required since all_dates is requested

        pass

    else:

        if weekly:

            # we wish to filter on Sundays because that is always the last day of each 'Year_week'
            # (for instance last day of week 20, 21, 22 etc. is always a Sunday). However, due to the
            # fact that earlier applied function 'add_calculated_cols' does a simple groupby('Year_week')
            # to obtain the aggregated weekly numbers, the first aggregation for each country will often
            # be based on less than seven days. So before filtering we will change the value of those cases

            for i in range(df.shape[0]):

                # looping dataframe, which is sorted by country then date

                # check if the current row is the first of a new country

                if i == 0:

                    new_country = True

                else:

                    if df.ISO[i] == df.ISO[i-1]:

                        new_country = False

                    else:

                        new_country = True

                # if it is we find the row of the first '6', which could be on the current row
                # or any of the next six rows.
                # We change its value unless the weekday is '0' (in which case the first '6' will
                # be the seventh element, and we do not have to change its value)

                if new_country:

                    wd = df.Weekday[i]

                    if wd > 0:

                        diff = 6 - wd
                        df.Weekday[i + diff] = 0

            # Finally we filter the dataframe on Sundays

            df = df[df.Weekday == 6]

        else:

            # In this case we have neither asked for all dates nor weekly dates,
            # which means we will get the last date only.

            df = df[df.Date == df.Date.max()].reset_index(drop=True)


    # we set the dates as index and make sure it is in datetime format

    df = df.reset_index(drop=True).set_index('Date')
    df.index = pd.to_datetime(df.index, infer_datetime_format=True)

    return df

def select_continent(df, continent):
    '''
    This function filters the dataframe on a single continent

    Args:
        df (dataframe): Dataset including a column 'Continent'
        continent (string): Name of continent. Valid values are found in below list

    Returns:
        df_continent (dataframe): Dataframe with only data from a single contintent
    '''
    if continent:

        continent_list = ['America', 'Europe', 'Asia', 'Africa', 'Oceania']

        assert continent in continent_list, "Continent is not in continent_list"

        df_continent = df[df['Continent'] == continent]

    return df_continent


def rank_data(df_current, top_n = (None, None)):
    '''
    This function filters on the top n countries ranked on any of the following:

    - Population
    - Pop_km2
    - Urban_Population_ratio
    - Median_age
    - Deaths
    - Deaths_per_100k

    Args:
        df_current (dataframe): dataframe with just the latest date
        top_n (tuple): First element (str): variable name to base the ranking on
                        Second element (int): the n in top_n


    Returns:
        df (dataframe): ranked data
    '''

    var_list = ['Population', 'Pop_km2', 'Urban_Population_ratio', 'Median_age', 'Total_deaths', \
                'Total_deaths_per_100k', 'Deaths', 'Deaths_per_100k', 'Deaths_s7', 'Deaths_per_100k_s7',
                'Deaths_week', 'Deaths_lastweek', 'Infection_rate']

    # unpack tuple

    var = top_n[0]
    n = top_n[1]

    assert var in var_list

    # limiting n so that it is not more than the number of rows (capped)

    if n:
        tot_countries = df_current.shape[0]
        if n > tot_countries:
            n = tot_countries

    df = df_current.sort_values(by=[var], ascending=False)[:n]

    return df


def prepare_barplot(continent=None, top_n = (None, None)):
    '''
    This funtion gets the current high level aggregated data suitable for bar plots.
    It is optional to filter on continent.
    It is also optional to filter on the top n countries ranked on any of the following:

    - Population
    - Pop_km2
    - Urban_Population_ratio
    - Median_age
    - Deaths
    - Deaths_per_100k

    Args:
        continent (str): The continent ('America', 'Europe', 'Asia', 'Africa', 'Oceania')
        top_n (tuple): First element (str): variable name to base the ranking on
                        Second element (int): the n in top_n

    Returns:
        df_current (dataframe): dataframe with just the latest date prepared for barplot
    '''

    df_merged = merge_data()

    df_full = add_calculated_cols(df_merged)

    df_current = dates_choice(df_full)

    if continent:
        df_current = select_continent(df_current, continent)

    var_list = ['Population', 'Pop_km2', 'Urban_Population_ratio', 'Median_age', 'Total_deaths', \
                'Total_deaths_per_100k', 'Deaths', 'Deaths_per_100k', 'Deaths_s7', 'Deaths_per_100k_s7', \
                'Deaths_week', 'Deaths_lastweek', 'Infection_rate']

    # assert that top_n tuple input is valid in case two (no-None) elements are provided

    if (len(top_n) == 2) and (top_n[0] and top_n[1]):

        assert top_n[0] in var_list, "First tuple element in 'top_n' must be in var_list and of type String"
        assert isinstance(top_n[1], int) == True, "Second tuple element in 'top_n' must of type Integer"

        df_current = rank_data(df_current, top_n)

    df_current = df_current.reset_index().set_index('Country')

    return df_current

def prepare_time(continent=None, top_n = (None, None)):
    '''
    This funtion gets the daily data suitable for time series plots.
    It is optional to filter on continent.
    It is also optional to filter on the top n countries ranked on any of the following:

    - Population
    - Pop_km2
    - Urban_Population_ratio
    - Median_age
    - Deaths
    - Deaths_per_100k

    Args:
        continent (str) (optional): The continent ('America', 'Europe', 'Asia', 'Africa', 'Oceania')
        top_n (tuple) (optional): First element (str): variable name to base the ranking on
                        Second element (int): the n in top_n

    Returns:
        df_current (dataframe): dataframe with just the latest date prepared for barplot

    '''

    # getting the dataframe prepared with historic data

    df_merged = merge_data()

    df_full = add_calculated_cols(df_merged)

    df = dates_choice(df_full, all_dates=True)

    # defining the beginning of time to be 9th of March 2020
    df = df[df.index > '2020-03-08']


    # list of countries and number of countries

    countries = df.Country.unique()

    tot_countries = df.shape[0]

    # setting a default (key) variable 'var' in case none is provided
    var = 'Total_deaths'


    # updating the key variable 'var' and 'n' from the input (optional)

    if top_n[0] and top_n[1]:

        var = top_n[0]
        n = top_n[1]
        if n > tot_countries:
            n = tot_countries
    else:
        n = tot_countries


    # make list of countries ordered by 'var' at the latest date
    last_date = df.index.max()

    df_last = df[df.index == last_date].sort_values(var, ascending=False)

    countrylist = list(df_last['Country'][:n])

    # filter df to only contain the countries in the countrylist
    df = df[df['Country'].isin(countrylist)].reset_index()

    return countrylist, df


def prepare_time_weekly(continent=None, top_n = (None, None)):
    '''
    This funtion gets the daily data suitable for time series plots - weekly version.
    It is optional to filter on continent.
    It is also optional to filter on the top n countries ranked on any of the following:

    - Population
    - Pop_km2
    - Urban_Population_ratio
    - Median_age
    - Deaths
    - Deaths_per_100k

    Args:
        continent (str) (optional): The continent ('America', 'Europe', 'Asia', 'Africa', 'Oceania')
        top_n (tuple) (optional): First element (str): variable name to base the ranking on
                        Second element (int): the n in top_n

    Returns:
        df_current (dataframe): dataframe with historic weekly data

    '''

    # getting the dataframe prepared with historic data

    df_merged = merge_data()

    df_full = add_calculated_cols(df_merged)

    df = dates_choice(df_full, all_dates=False, weekly=True)

    # defining the beginning of time to be 9th of March 2020
    df = df[df.index > '2020-03-08']

    # list of countries and number of countries

    countries = df.Country.unique()

    tot_countries = df.shape[0]

    # setting a default (key) variable 'var' in case none is provided
    var = 'Total_deaths'


    # updating the key variable 'var' and 'n' from the input (optional)

    if top_n[0] and top_n[1]:

        var = top_n[0]
        n = top_n[1]
        if n > tot_countries:
            n = tot_countries
    else:
        n = tot_countries


    # make list of countries ordered by 'var' at the latest date
    last_date = df.index.max()

    df_last = df[df.index == last_date].sort_values(var, ascending=False)

    countrylist = list(df_last['Country'][:n])

    #df = df.reset_index()
    df = df[df['Country'].isin(countrylist)]


    return countrylist, df


def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing plotly visualizations

    """


    graph_one = []
    df = prepare_barplot()
    df = df.reset_index()
    df = df[['Country', 'ISO', 'Total_deaths']]
    df.sort_values('Total_deaths', ascending=False, inplace=True)

    graph_one.append(
        go.Choropleth(
            locations = df['ISO'],
            z = df['Total_deaths'],
            text = df['Country'],
            colorscale = 'Viridis_r',
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Deaths',
            colorbar_ticksuffix = '',
            )
        )

    layout_one = dict(
        title = 'All Countries: Total deaths',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
            )
        )

    graph_two = []
    countrylist, df = prepare_time(top_n = ('Total_deaths', 15))

    #df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Total_deaths.tolist()
      graph_two.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_two = dict(title = 'Total deaths',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Deaths'),
                xaxis_rangeslider_visible=True)



    graph_three = []
    countrylist, df = prepare_time(top_n = ('Total_deaths_per_100k', 10))

    #df = df[df.Country.isin(countrylist)]

    for country in countrylist:
      x_val = df[df['Country'] == country].Date.tolist()
      y_val =  df[df['Country'] == country].Total_deaths_per_100k.tolist()
      graph_three.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

    layout_three = dict(title = 'Total deaths per 100,000 people',
                xaxis = dict(title = 'Date'),
                yaxis = dict(title = 'Deaths'),
                xaxis_rangeslider_visible=True)





    # append all charts to the figures list
    figures = []

    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))


    return figures
