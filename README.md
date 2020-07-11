### Capstone Project:

# 2020 Pandemic and the Curious Case of Sweden

#### By Truls Møller 2020-07-07

### Table of Contents


* [Project Definition](#chapter2)
    * [Project Overview](#section_2_1)
    * [The Data](#section_2_2)   
    * [Project Statement](#section_2_3)
    * [Metrics](#section_2_4)
* [Conclusion](#chapter6)
* [Improvement](#chapter7)

### Project Definition <a class="anchor" id="chapter2"></a>

https://pandemic2020.herokuapp.com/
Webapp hosted on Heroku displaying Choropleth visualizations on a world map of the current COVID-19 death toll both in absolute terms and in relative terms. There are also some time series charts showing the development over time.

It is built with a Python 3 backend. Visualizations brought to the frontend using plotly, flask, js and bootstrap. Please see requirements.txt for detailed list of requirements.

#### Project Overview  <a class="anchor" id="section_2_1"></a>

The origin of the project were two things:

    1. My frustration over lack of death numbers in the media to provide a good picture of the situation
    2. Compassion with my neighbor country of Sweden, where there has not been any degree of lockdown,
       and now the death toll is more than 10x of my own country Norway.

It seems important to get a sober picture and look into the data myself, and even learn some things about this aspect of the healthcare domain.

The data will be the widely used dataset compiled by John Hopkins University. The data gets downloaded using a funtion in the Jupyter Notebook. It gets downloaded from a Kaggle user who has shared it there, but it comes originally from John Hopkins University.




#### Data <a class="anchor" id="section_2_2"></a>

Sources for datasets:

Updated through this notebook:
- covid-19 related datasets will be connected to this Kaggle user Sudalairaj Kumar, it originates from John Hopkins University.: https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset/discussion/136061

Downloaded once:
- population_by_country: https://www.kaggle.com/tanuprabhu/population-by-country-2020
    I have manually added some ISO country codes, changed country names to fit with the corresponding country names used in the covid-19 dataset and stored it in the data folder as 'population_2020_for_johnhopkins_data.csv'
- natural earth polygon shapes of countries: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/

#### Problem Statement  <a class="anchor" id="section_2_3"></a>

    1. What is the current global picture of how many lives have been lost to the COVID-19 virus?

    2. Looking at the top 10 countries based on highest number of deaths relative to population, how has the development been over time?

    3. How is Sweden's R value developing, and how does it compare to its neighboring countries?

    4. What scenarios lie ahead for Sweden?


#### Metrics    <a class="anchor" id="section_2_4"></a>


    1. 'Population'
    2. 'Total_deaths'
    3. 'Total_deaths_per_100k' (derived from 'Total_deaths' and 'Population')
    4. 'Deaths'                (derived from 'Total_deaths', means new daily)
    5. 'Deaths_per_100k'       (derived from 'Deaths' and 'Population')
    6. 'Deaths_s7'             (derived from 'Deaths')
    7. 'Deaths_per_100k_s7'    (derived from 'Deaths_per_100k')
    8. 'Deaths_week'           (derived from 'Deaths', means sum of new daily for the past 7 days)
    9. 'Deaths_lastweek'       (derived from 'Deaths', means sum of new daily for the past 14-8 days)
    10. 'Infection_rate'       (derived from 'Deaths_week' and 'Deaths_lastweek')

    Assumption: R can be estimated from the ratio week-over-week deaths:

               R = Deaths_week_n/Deaths_week_n_minus_1

           This again is based on the assumption that a fixed ratio of the truly infected dies.
           And the assumption that a typical tranfer rate from one human to the next of seven days.

    Comment: My first idea to calculate infection rate R was the more natural choice, namely to take  

            Infected_week_n/Infected_week_n_minus_1.

        Natural choice because the true infection number, if we knew it, would yield the true R.
        However, since infected number are less trustworthy than the death numbers and more liable to vary from
        country to country, I decided the chosen estimation method of R is much better.

        This is also based on incubation time, and using weekly sums, there will be a smoothing effect, which
        should reduce some noise in the trend curve (weekly seasonality).

### Conclusion <a class="anchor" id="chapter6"></a>

I think I managed to show that it is possible to understand the dynamics of the decease by simply focusing on the 'Deaths' statistic and derive an estimate of the infection rate (R) from that.

We saw that how Sweden stood out from the other Nordic countries with their less strict policies when it came to lockdown and social distancing. I showed some future scenarios, and we saw the huge difference from R of 0.9 to R of 0.7. End date will be around 1-Dec this year instead of 1-Nov 2021! Deaths will be 326 instead of 1259. That is almost a thousand lives!

So, for the sake of the Swedish citizens, I really hope the Swedish government can implement some degree of lockdown, until an R of around 0.7 (or lower) is achievable.

### Improvement <a class="anchor" id="chapter7"></a>

Some ideas to improve / build on this project:

    - Add some climate data to check whether climate matters for the virus spread
    - Add data from blood samples (are there anomalies in iron, vitamin levels etc. for those who get hospitalized?)
    - Add more advanced model / machine learning layer
    - Over time check for signs that the virus might get weaker or stronger in terms of how deadly it is.
