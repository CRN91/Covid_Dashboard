# Covid_Stats_Dashboard
A covid-19 web dashboard that displays relevant news articles and stats about covid-19.

Documentation for all the files and functions is available in covid_dashboard/docs/_build/html/index.html.

requirements.txt contains all imported modules required to run the code.

MIT License available to read in covid_dashboard/LICENSE.txt .

To use the application run main.py found in covid_dashboard/dashboard/ and head to http://127.0.0.1:5000/ in a web browser.

To get news updates enter your api key (you can get one from here: https://newsapi.org/) in config.json, found in covid_dashboard/dashboard/ , as the value for api_key.

In the config file you can change the location that the covid updates are for according to location codes found here: https://coronavirus.data.gov.uk/details/developers-guide.

To change the national data or local data the name of the area is needed, along with the area type code, currently only 'ltla' and 'nation' codes are supported.

Feel free to use this code as you wish and commits are welcomed!
