# HopScotch: A Scotch Whisky Recommendation System

Scotch whisky is a massively popular spirit produced in Scotland and exported throughout the world.  Distilleries 
pride themselves on crafting products that are complex and unique.  For newcomers, navigating the descriptions of 
different scotches can be intimidating and confusing.  Finding a new favorite scotch might involve a great deal of 
trial and error, and since individual bottles can easily cost over 100 USD, this can involve significant financial 
risk.

HopScotch is a recommendation system that characterizes over 1000 single malt scotch whiskies using categorical and 
text data.  Given a user's past positive and negative experiences with products in the database, it uses cosine 
similarity to recommend 10 new scotches most suited to the user's taste, along with information about what tasting 
notes each shared with the input liked scotches.

The HopScotch web-app is available at www.hop-scotch.tech

## REPO Structure
* /HopScotch_WebApp <br>
Contains Python script based on Flask as well as HTML, css, js files used to generate the HopScotch web app.

* /Data <br>
Contains dumpfile of PostgreSQL database used for HopScotch web app.

* /Jupyter_Notebooks <br>
This folder contains three Jupyter notebooks that were used in the development of HopScotch, as well as data saved in csv and json formats.  The Data_Collection notebook contains all code used to scrape information from the website of the vendor www.masterofmalt.com.  The Data_Cleaning_EDA notebook contains code used to clean and organize this data, as well as some preliminary investigations of trends.  The Recommendation_Model notebook contains the code implementing the model used to make recommendations and the validation tests used to measure success.
