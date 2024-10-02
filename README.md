# Covid 19 Information Dashboard

<img src="rmimg/ECM1400.svg" height="28"> <img src="rmimg/Solo.svg" height="28">

A Covid-19 web dashboard that displays relevant news articles and stats about Covid-19 for the continuous assessment of the Programming module taught by Dr Matt Collison.

## Installation

Requires Python 3.x and the libraries:

1. "flask"
2. "newsapi"
3. "uk-covid19"

A `requirements.txt` with all importated modules is included for ease of installation.

## Configuration

In the directory `covid_dashboard/dashboard/` you can edit the `config.json` file. Include your newsapi key (new ones can be found [here](https://newsapi.org/)) for access to news articles relating to Covid-19. Here you can also change the location that the Covid updates are for according to location codes found [here](https://coronavirus.data.gov.uk/details/developers-guide). To change the national data or local data the name of the area is needed, along with the area type code, currently only 'ltla' and 'nation' codes are supported.

## Usage

To use the application run `main.py` found in `covid_dashboard/dashboard/` and head to http://127.0.0.1:5000/ in a web browser.

## Documentation

Documentation for all the files and functions is available in the file `covid_dashboard/docs/_build/html/index.html`.

## License

[MIT](https://choosealicense.com/licenses/mit/)
