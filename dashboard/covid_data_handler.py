"""This module was designed specifically to be used by a covid-19 dashboard application and
   contains functions to request covid data from uk_covid19 api, process it and send them to the UI.
"""
import logging
import typing
import pandas as pd
from uk_covid19 import Cov19API, exceptions
from requests.exceptions import ConnectionError as requestsConnectionError
import dashboard.scheduler_updater as us
import dashboard.covid_news_handling as cnh
import dashboard.config_handler as ch

display_covid = {}

def parse_csv_data(csv_filename: str) -> list:
    """Takes in a csv filename and returns a list with each item being a new line of the file.

       :param csv_filename: The name of a csv filename, '.csv' appendix is optional
       :type csv_filename: str

       :return: A list of strings with each item being a single line of the csv file
       :rtype: list
    """
    logging.info("starting parse_csv_data function")
    csv_filename = str(csv_filename)  # Makes sure input is a string
    if csv_filename[-4:] != ".csv":  # Checks if the filename has the
        csv_filename += ".csv"       # '.csv' appendix and appends it if necessary

    with open(csv_filename, "r", encoding='utf-8') as data:
        logging.info("parse_csv_data function finished")
        return [word.split()[0] for word in data.read().splitlines()]
        # returns data as a list of strings for each row in the csv file


def process_covid_csv_data(covid_csv_data: list) -> typing.Optional[tuple]:
    """Takes covid data and returns last 7 days of cases, cumulative hospital cases and deaths.

       Takes covid data as a list of strings as returned by parse_csv_data function, where each
       word in a string represents a data value with the first row being the headers of each column.
       This function converts this data into a pandas dataframe to organise the data and then
       returns a tuple containing the sum of the last 7 days of cases, the current cumulative
       amount of hospital cases and the cumulative deaths.

       :parameter covid_csv_data: covid data as returned by parse_csv_data function
       :type covid_csv_data: list

       :return: The sum of the last 7 days of covid cases, the cumulative amount of hospital cases
                and the cumulative amount of deaths or None
       :rtype: tuple or None
    """
    logging.info('starting process_covid_csv_data function')
    covid_csv_data = [word.split(',') for word in covid_csv_data]
    # Converts list of strings into list of lists as required by pandas dataframe

    covid_dataframe = pd.DataFrame(covid_csv_data[1:], columns=covid_csv_data[0])
    # Processes data into a pandas data frame

    for cum_deaths in covid_dataframe['cumDailyNsoDeathsByDeathDate']:
        if cum_deaths != '':  # searches for the first none '' value
            for index, cases in enumerate(covid_dataframe['newCasesBySpecimenDate']):
                if cases != '':  # searches for first none '' value
                    logging.info('process_covid_csv_data function finished')
                    return pd.to_numeric(covid_dataframe['newCasesBySpecimenDate']
                                         [index+1:index+8]).sum(), \
                                         int(covid_dataframe['hospitalCases'][0]), int(cum_deaths)
                # sum of cases from index+1, as the first value is always incomplete data, to
                # index+8 to get the sum of 1 week of cases. The latest hospital cases represents
                # the cumulative hospital cases and cum deaths is cumulative deaths.
    return None


def covid_API_request(location: str = 'Exeter', location_type: str = 'ltla',
                      dictionary: bool = True) -> dict or pd.DataFrame:
    """Takes location data and returns covid data requested from the uk_covid19 API.

       Makes a request to the uk covid-19 API for the daily cases, hospital cases and
       the cumulative deaths (if applicable) by date and area and returns the data as
       either a pandas dataframe or a dictionary with the date as the key and all other
       data as the values.

       :parameter location: Location name according to
                            "https://coronavirus.data.gov.uk/details/developers-guide",
                            default value is 'Exeter'
       :type location: str, optional
       :parameter location_type: Location type according to
                  "https://coronavirus.data.gov.uk/details/developers-guide",
                  default value is 'ltla'
       :type location: str, optional
       :parameter dictionary: True if you require a dictionary to be returned, False if you
                              prefer a pandas dataframe, default value is True
       :type dictionary: boolean, optional

       :return: returns a dictionary of covid data with the date as the key or a dataframe
                with covid data
       :rtype: dict or pandas dataframe
    """
    logging.info('starting covid_API_request function')

    data = {"areaName": "areaName",  # data parameter for covid api, gives specified data
            "date": "date",
            "daily cases": "newCasesBySpecimenDate",
            }

    if location_type == 'nation':  # we need extra data points from the nation request
        data["hospital cases"] = "hospitalCases"
        data["total deaths"] = "cumDeaths28DaysByPublishDate"

    elif location_type not in ["overview", "region", "ltla", "utla", "nhsRegion"]:
        # uk_covid-19 api only accepts these location types
        logging.error("location_type: %s is not compatible with the covid API", location_type)
        return None

    area = ['areaType='+location_type,
            'areaName='+location
            ]
    try:
        data = Cov19API(filters=area, structure=data).get_csv().splitlines()
        # sends request for a csv file from api with .get_csv and then splits it by each line
        if not data:
            logging.error("Covid 19 API has returned an empty list")
            return None
    except exceptions.FailedRequestError:  # requested data not received
        logging.exception("uk_covid19 API has returned an exception to the request")
        return None
    except requestsConnectionError:  # couldn't connect to the api
        logging.exception("failed to connect to the uk_covid19 API")
        return None

    for i, line in enumerate(data):
        data[i] = line.split(',')  # splits it into a list of lists for the pandas library
    covid_data = pd.DataFrame(data[1:], columns=data[0])  # columns are taken from the first row

    weekly_cases = []
    daily_cases = pd.to_numeric(covid_data['daily cases'])  # turns data from str to float
    for i in range(len(daily_cases)):
        if i > len(daily_cases)-7:  # for the first 6 values there is not enough data for week sum
            weekly_cases.append(str(daily_cases[i:].sum()))
        else:
            weekly_cases.append(str(daily_cases[i:i+7].sum()))
    covid_data['weekly cases'] = weekly_cases  # adds weekly cases to dataframe under a new column

    if dictionary:  # data requested in dict format
        logging.info("covid_API_request function finished, returning dictionary")
        return covid_data.set_index('date').T.to_dict()  # converts to a dictionary and returns

    logging.info("covid_API_request function finished, returning pandas dataframe")
    return covid_data  # returns data as a pandas dataframe


def first_non_null(iterable: list) -> typing.Optional[str]:
    """Takes in an iterable, returns the first item that is not equal to '', if not found then None.

       :parameter iterable: A list that a for loop can iterate over
       :type iterable: list

       :return: The first item that is not equal to '' in the list or None if none is found
       :rtype: str or None
    """
    for i in iterable:
        if i != '':
            return str(i)
    return None


def update_covid(event_title: typing.Optional[str] = None, repeat: typing.Optional[bool] = None):
    """Calls for data from covid_API_request and formats it to be used by Jinja2 in the webpage.

       Calls for covid-19 data from the uk covid-19 API and formats it to be used by flask when
       rendering the html for the dashboard. This function update_covid can be called in two places,
       either on its own to run an update or by the sched module's scheduler. When called by the
       scheduler the parameters 'event_title' and 'repeat' of the event that called it are needed so
       the event can be removed from the scheduler or repeated for the next day. 'display_covid' is
       a global variable as the sched module can not store anything that is returned when it runs
       its event's functions so to access the covid data you must import 'display_covid'.

       :parameter event_title: The title of the scheduler event
       :type event_title: str, optional
       :parameter repeat: The value associated with whether an event needs to repeat
       :type repeat: bool, optional
    """
    logging.info('starting update_covid procedure')

    config = config_location()  # loads location from config

    if config['local_name'] is None:  # if there is no config location it runs defaults
        local_data = covid_API_request(dictionary=False)
    else:
        local_data = covid_API_request(location=config['local_name'],
                                       location_type=config['local_type'], dictionary=False)
    national_data = covid_API_request(location=config['nation_name'],
                                      location_type=config['nation_type'], dictionary=False)
    logging.debug("local data = %s", local_data)
    logging.debug("national data = %s", national_data)

    display_covid_updater(local_data, national_data)  # updates display_covid

    if event_title:  # if update_covid is called through the scheduler the event is to be processed
        us.process_event(update_covid, event_title, repeat)

def schedule_covid_updates(update_interval: str or int, update_name: str,
                           repeat: typing.Optional[bool] = None, category: str = 'covid',
                           blacklist_news: typing.Optional[list] = None):
    """Updates the scheduler and schedules, also sending the update to the config file.

       Creates events in the scheduler and also updates a list of dictionaries with each dict
       representing an event in the scheduler, this is used to be able to store the events in
       the config and load them back into the scheduler and for data to be displayed on the
       dashboard UI. A unique name is created from user input and the time in seconds until the
       event needs to run is calculated and this data is used to create the event. This function
       can both schedule news updates and covid updates and is only named 'schedule_covid_updates'
       to fit specification.

       :parameter update_interval: The user selected time for the event to be run by the scheduler,
                                   if string, argument is expected in 24 hour clock format e.g.
                                   '00:00'. If integer, argument is time in seconds
       :type update_interval: str or int
       :parameter update_name: The user selected label for the event to be run by the scheduler
       :type update_name: str
       :parameter repeat: The value associated with whether an event needs to repeat
       :type repeat: bool, optional
       :parameter category: The category of the update, currently only accepts 'covid' or 'news',
                            default value is 'covid'
       :type category: str, optional
       :parameter blacklist_news: A list of news article titles that have been blacklisted
       :type blacklist_news: list, optional

       :raise ValueError: A value error is raised if the argument passed is not an int or str
    """
    logging.info("starting schedule_covid_updates procedure")

    if category == 'covid':
        function = update_covid
    elif category == 'news':
        function = cnh.update_news
#    elif category == 'test':
 #       function =

    if isinstance(update_interval, str):  # string is expected in 24 hour format '00:00'
        time_seconds = us.difference_seconds(update_interval)
        content = 'at '+update_interval  # format to be displayed by ui
    elif isinstance(update_interval, int):  # int is expected to represent time in seconds
        time_seconds = update_interval
        content = f'in {time_seconds} seconds'  # format to be displayed by ui
    else:
        logging.exception("argument 'update_interval' expected as a string or integer not %s",
                          type(update_interval))
        raise ValueError

    name, update_name = us.unique_name(update_name, category)  # gets a unique name
    logging.debug("name: %s", update_name)
    if update_name:
        if category == 'covid':
            us.update_scheduler.enter(time_seconds, 1, function, (name, repeat))
        else:  # update_news function requires extra argument blacklist_news
            us.update_scheduler.enter(time_seconds, 1, function, (blacklist_news, name, repeat))

        us.schedules.append({'title': name, 'content': content,
                             'name': update_name, 'category': category,
                             'repeat': repeat
                             })
        # events have to be stored in this format to be compatible with json files
        logging.info("schedule added to list")

    ch.config_update(us.schedules)  # updates config file with new schedules


def config_location() -> dict or typing.Optional[dict]:
    """Loads config location data and checks for any errors, if there are None is returned.

       :return: Config location data or None
       :rtype: dict or None
    """
    location = {'local_name': None, 'local_type': None, 'nation_name': 'england',
                'nation_type': 'nation'}  # default values
    try:
        config = ch.json_load()['location']  # checks config for location data and will set
    except KeyError:                         # arguments here for the uk_covid19 api request
        return location

    try:
        local_name_temp = config['local_name']  # can only change values from default if
        local_type_temp = config['local_type']  # they're not equal to None
        if local_name_temp is not None and local_type_temp is not None:
            location['local_name'] = local_name_temp
            location['local_type'] = local_type_temp
    except KeyError:
        pass

    try:
        nation_name_temp = config['nation_name']
        nation_type_temp = config['nation_type']
        if nation_name_temp is not None and nation_type_temp is not None:
            location['nation_name'] = nation_name_temp
            location['nation_type'] = nation_type_temp
    except KeyError:
        pass

    return location

def display_covid_updater(local_data: pd.DataFrame, national_data: pd.DataFrame):
    """Updates the values in the global variable display_covid with data requested from the api.

       :parameter local_data: data referring to the local area selected
       :type local_data: pandas DataFrame
       :parameter national_data: data referring to the national area selected
       :type national_data: pandas DataFrame
    """
    logging.info("starting display_covid_updater procedure")

    if not isinstance(local_data, type(None)):  # local data is sent to display_covid
        display_covid['local_name'] = local_data['areaName'][0]
        display_covid['local_weekly_cases'] = first_non_null(local_data['weekly cases'])
        display_covid['local_rate'] = int(float(display_covid['local_weekly_cases'])/7)
        # takes 7 day average
    else:  # used to display an error on the ui
        display_covid['local_name'] = None
        display_covid['local_weekly_cases'] = None
        display_covid['local_data'] = {'areaName': [None]}
        display_covid['local_rate'] = 'error'

    if not isinstance(national_data, type(None)):
        display_covid['national_name'] = national_data['areaName'][0]
        display_covid['national_weekly_cases'] = first_non_null(national_data['weekly cases'])
        display_covid['hospital_cases'] = 'Hospital cases: '\
                                          +first_non_null(national_data['hospital cases'])
        display_covid['total_deaths'] = 'National Deaths: '\
                                        +first_non_null(national_data['total deaths'])
        display_covid['national_rate'] = int(float(display_covid['national_weekly_cases'])/7)
        # takes 7 day average
    else:
        display_covid['national_name'] = None
        display_covid['national_weekly_cases'] = None
        display_covid['hospital_cases'] = 'Hospital cases: error'
        display_covid['total_deaths'] = 'National Deaths: error'
        display_covid['national_data'] = {'areaName': [None]}
        display_covid['national_rate'] = 'error'

    logging.debug('covid display data = %s', display_covid)
