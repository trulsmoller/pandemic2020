### Capstone Project:

# 2020 Pandemic and the Curious Case of Sweden

#### By Truls Møller 2020-07-07

### Table of Contents


* [Project Definition](#chapter2)
    * [Project Overview](#section_2_1)
    * [The Data](#section_2_2)   
    * [Project Statement](#section_2_3)
    * [Metrics](#section_2_4)
* [Results](#chapter5)
* [Conclusion](#chapter6)
* [Improvement](#chapter7)

### Project Definition <a class="anchor" id="chapter2"></a>

#### Project Overview  <a class="anchor" id="section_2_1"></a>

The origin of the project were two things:

    1. My frustration over lack of death numbers in the media to provide a good picture of the situation
    2. Compassion with my neighbor country of Sweden, where there has not been any degree of lockdown,
       and now the death toll is more than 10x of my own country Norway.

It seems important to get a sober picture and look into the data myself, and even learn some things about this aspect of the healthcare domain.

The data will be the widely used dataset compiled by John Hopkins University. We will be downloading the data from a Kaggle user who has shared it there, but it comes from John Hopkins University.

### Description
Webapp hosted on Heroku. https://pandemic2020.herokuapp.com/

This project will be work in progress for a while, as the pandemic unfolds. The underlying data gets updated daily.

Python backend. Visualizations brought to the frontend using plotly, flask, js and bootstrap. Please see requirements.txt for detailed list of requirements.

### Data

Sources for datasets:

Updated through this notebook:
- covid-19 related datasets will be connected to this Kaggle user Sudalairaj Kumar, it originates from John Hopkins University.: https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset/discussion/136061

Downloaded once:
- population_by_country: https://www.kaggle.com/tanuprabhu/population-by-country-2020
    I have manually added some ISO country codes, changed country names to fit with the corresponding country names used in the covid-19 dataset and stored it in the data folder as 'population_2020_for_johnhopkins_data.csv'
- natural earth polygon shapes of countries: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
