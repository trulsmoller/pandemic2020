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
    This function unzips the compressed new data file found in the 'data' folder
    in the root directory of the web app. Then the zip file is deleted.

    Args:
        file_name (str): name of covid-19 data file
        file_path (str): path to covid-19 data file

    Returns:
        this function does not return anything
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
        df_full (dataframe): With new columns added
    '''

    df_full = df_merged.copy()

    df_full['Total_deaths_per_100k'] = 100000*df_full['Total_deaths']/(df_full['Population'] + 1.0)

    df_full['Deaths'] = 0.0
    df_full['Deaths_per_100k'] = 0.0
    df_full['Deaths_s7'] = 0.0
    df_full['Deaths_per_100k_s7'] = 0.0
    df_full['Deaths_week'] = 0.0
    df_full['Deaths_lastweek'] = 0.0
    df_full['Infection_rate'] = 0.0

    country_list = df_full.Country.unique().tolist()

    for country in country_list:


        df_temp = df_full.loc[df_full.Country == country]

        df_temp['Shift1'] = df_temp.Total_deaths.shift(1).fillna(0)
        df_temp['Deaths'] = df_temp['Total_deaths'] - df_temp['Shift1']

        df_temp['Deaths_shift1'] = df_temp['Deaths'].shift(1).fillna(0)
        df_temp['Deaths_shift2'] = df_temp['Deaths'].shift(2).fillna(0)
        df_temp['Deaths_shift3'] = df_temp['Deaths'].shift(3).fillna(0)
        df_temp['Deaths_shift4'] = df_temp['Deaths'].shift(4).fillna(0)
        df_temp['Deaths_shift5'] = df_temp['Deaths'].shift(5).fillna(0)
        df_temp['Deaths_shift6'] = df_temp['Deaths'].shift(6).fillna(0)




        df_temp['Deaths_week'] = (df_temp['Deaths'] + df_temp['Deaths_shift1'] \
                                     + df_temp['Deaths_shift2'] + df_temp['Deaths_shift3'] \
                                     + df_temp['Deaths_shift4'] + df_temp['Deaths_shift5'] \
                                     + df_temp['Deaths_shift6']).astype(int)

        df_temp['Deaths_lastweek'] = df_temp['Deaths_week'].shift(7).fillna(0)

        df_temp['Infection_rate'] = (df_temp['Deaths_week']/df_temp['Deaths_lastweek']).fillna(0).replace([np.inf, -np.inf], 0)

        df_temp['Deaths_s7'] = (df_temp['Deaths_week']/7.0).astype(int)

        df_temp.drop(['Shift1', 'Deaths_shift1', 'Deaths_shift2', 'Deaths_shift3', \
                      'Deaths_shift4', 'Deaths_shift5', 'Deaths_shift6'], axis=1, inplace=True)


        df_temp['Deaths_per_100k'] = 100000*df_temp['Deaths']/(df_temp['Population'] + 1.0)
        df_temp['Deaths_per_100k_s7'] = 100000*df_temp['Deaths_s7']/(df_temp['Population'] + 1.0)

        index_list = df_temp.index

        for i in index_list:
            df_full.loc[i,'Deaths'] = df_temp.loc[i,'Deaths']
            df_full.loc[i,'Deaths_s7'] = df_temp.loc[i,'Deaths_s7']

            df_full.loc[i,'Deaths_per_100k'] = df_temp.loc[i,'Deaths_per_100k']
            df_full.loc[i,'Deaths_per_100k_s7'] = df_temp.loc[i,'Deaths_per_100k_s7']
            df_full.loc[i,'Deaths_week'] = df_temp.loc[i,'Deaths_week']
            df_full.loc[i,'Deaths_lastweek'] = df_temp.loc[i,'Deaths_lastweek']
            df_full.loc[i,'Infection_rate'] = df_temp.loc[i,'Infection_rate']


    return df_full

def dates_choice(df, all_dates=False, specific_date=None):
    '''
    This function filters and transforms the dataset into one of two different dataset types
    based on the True/False value provided as 'all_dates' argument:

    1. Historic data (all_dates=True)
    2. Single date data (all_dates=False)

    The historic data will be suitable for performing time series analysis, and for this purpose
    the columns 'New_deaths' and 'New_deaths_per_100k' are added. The latter is also smoothed
    applying a 7-day moving average on the daily new deaths reported. This effectively removes
    the weekly seasonality.

    The single date data will be suitable to look at the overall picture (such as accumulated death
    count per country). By default the date will be the last date. However, one can also input
    a 'specific_date' to override the default.

    Note: The specific_date input will be ignored if used in combination with historic seach
    (all_dates=True).

    Args:
        df (dataframe): df containing covid-19 data as well as population data

        all_dates (boolean): Optional argument - True if you wish to get all the historic data

        specific_date (string): Optional argument - If all_dates is False, you may input a 'yyyy-mm-dd'
        string in order to override the default behaviour which gets you the latest date.

    Returns:
        df_filtered (dataframe): Filtered dataframe with added attributes in case of the historic option.
    '''

    if not all_dates:

        if specific_date:

            df = df[df.Date == specific_date].reset_index(drop=True)
        else:
            df = df[df.Date == df.Date.max()].reset_index(drop=True)

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


def rank_data(df_current, var, top_n = None):
    '''
    This function filters on the top n countries ranked on any of the following:

    - Population
    - Pop_km2
    - Urban_Population_ratio
    - Median_age
    - Deaths
    - Deaths_per_100k

    Args:
        file_name (str): name of covid-19 data file
        file_path (str): path to covid-19 data file

    Returns:
        this function does not return anything
    '''

    var_list = ['Population', 'Pop_km2', 'Urban_Population_ratio', 'Median_age', 'Total_deaths', \
                'Total_deaths_per_100k', 'Deaths', 'Deaths_per_100k', 'Deaths_s7', 'Deaths_per_100k_s7',
                'Deaths_week', 'Deaths_lastweek', 'Infection_rate']
    assert var in var_list

    if top_n:
        tot_countries = df_current.shape[0]
        if top_n > tot_countries:
            top_n = tot_countries

    df = df_current.sort_values(by=[var], ascending=False)[:top_n]

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
        file_name (str): name of covid-19 data file
        file_path (str): path to covid-19 data file

    Returns:
        this function does not return anything
    '''

    df_merged = merge_data()

    #df_full = add_calculated_cols(df_merged)

    df_current = dates_choice(df_merged, all_dates=False)

    if continent:
        df_current = select_continent(df_current, continent)

    var_list = ['Population', 'Pop_km2', 'Urban_Population_ratio', 'Median_age', 'Total_deaths', \
                'Total_deaths_per_100k', 'Deaths', 'Deaths_per_100k', 'Deaths_s7', 'Deaths_per_100k_s7', \
                'Deaths_week', 'Deaths_lastweek', 'Infection_rate']

    # assert that top_n tuple input is valid in case two (no-None) elements are provided

    if (len(top_n) == 2) and (top_n[0] and top_n[1]):

        assert top_n[0] in var_list, "First tuple element in 'top_n' must be in var_list and of type String"
        assert isinstance(top_n[1], int) == True, "Second tuple element in 'top_n' must of type Integer"

        df_current = rank_data(df_current, top_n[0], top_n[1])

    df_current = df_current.reset_index()
    #.set_index('Country')

    return df_current


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
    df.sort_values('Deaths_per_100k', ascending=False, inplace=True)

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







    # append all charts to the figures list
    figures = []

    figures.append(dict(data=graph_one, layout=layout_one))


    return figures
