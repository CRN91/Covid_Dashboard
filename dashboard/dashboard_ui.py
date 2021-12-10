"""This module was designed specifically to be used by a covid-19 dashboard application and
   contains functions to manage the user interface of the application.
"""
import logging
from json import JSONDecodeError
from flask import Flask, render_template, url_for, request, redirect
import dashboard.config_handler as ch
import dashboard.scheduler_updater as us
import dashboard.covid_data_handler as cdh
import dashboard.covid_news_handling as cnh

app = Flask(__name__)


def setup():
    """Loads or creates a config file and gets the initial covid and news data.

       Setup for the dashboard, loads / creates a config file and makes the initial covid data and
       news articles requests.
    """
    logging.info("starting first run setup")
    ch.json_create()  # creates config file if one does not exist
    try:
        config_load()
    except JSONDecodeError:  # if config file loads incorrectly the file is overwritten
        ch.json_create(overwrite=True)

    # gets initial covid data and news articles
    cdh.update_covid()
    cnh.update_news([])

    logging.info("first run setup complete")

def form_processing():
    """Requests website form submission data and sends it to a function to become schedule events.

       Gets the user input from the webpage and calls for a covid data update event and or a news
       update event to be created for the scheduler depending on the user input. If neither are
       called no events are created.
    """
    logging.info("starting form_processing procedure")
    form_submission = {'label': request.args.get("two"), 'time': request.args.get("update"),
                       'news': request.args.get("news"),
                       'covid_data': request.args.get("covid-data"),
                       'repeat_update': request.args.get("repeat")
                       }  # all requests from flask
    logging.debug('form submission: %s', form_submission)
    if form_submission['covid_data']:  # schedules a covid update if requested
        try:
            cdh.schedule_covid_updates(form_submission['time'], form_submission['label'],
                                       form_submission['repeat_update'], 'covid')
        except ValueError:
            logging.exception("Exception when trying to run schedule_covid_updates")
    if form_submission['news']:  # schedules a news update if requested
        try:
            cdh.schedule_covid_updates(form_submission['time'], form_submission['label'],
                                       form_submission['repeat_update'], 'news')
        except ValueError:
            logging.exception("Exception when trying to run schedule_covid_updates")

@app.route('/index', methods=['GET'])
def home():
    """Webpage loop, checks for user input to be processed and renders the html.

       Main webpage loop found at address '/index'. Checks for user input and calls processing
       procedures if necessary, runs the event scheduler and renders the html filling in missing
       data.

       :return: Rendering of the main webpage index.html, with all arguments passed to jinja2
       :rtype: flask render_template function
    """
    logging.debug("starting home page loop")

    if 'blacklist_news' not in locals():  # first run setup initiates local variable blacklist_news
        blacklist_news = []

    if request.args.get("two"):  # user cannot submit unless the label field has been filled
        logging.info("form submission request received")
        form_processing()

    close_news_title = request.args.get("notif")
    if close_news_title:  # runs when the user requests to remove a news title
        logging.info("close news request received")
        logging.debug("blacklisted news before = %s", blacklist_news)
        blacklist_news = cnh.close_news(close_news_title, blacklist_news)
        logging.debug("blacklisted news after = %s", blacklist_news)

    close_sched_title = request.args.get("update_item")
    if close_sched_title:  # runs when the user requests to remove a schedule event
        logging.debug("close schedule request received")
        us.close_schedule(close_sched_title)
        ch.config_update(us.schedules)

    logging.debug("running scheduler")
    us.update_scheduler.run(blocking=False)
    logging.debug('schedule queue: %s', us.update_scheduler.queue)

    try:
        if cnh.display_news[0]['title'] == 'Error':  # will try to auto reconnect every home rerun
            logging.warning("No connection to newsapi has been made, retrying connection.")
            cnh.update_news(blacklist_news)
    except IndexError:
        pass
    if cdh.display_covid['local_name'] is None or cdh.display_covid['national_name'] is None:
        logging.warning("No connection to uk_covid-19 has been made, retrying connection.")
        cdh.update_covid()  # will try to auto reconnect every flask home rerun (60 seconds)

    logging.debug("display_news = %s", cnh.display_news)
    logging.debug("display_covid = %s", cdh.display_covid)
    logging.info("finishing home page loop; rendering template")
    return render_template('index.html', location=cdh.display_covid['local_name'],
                                         local_7day_infections=cdh.display_covid['local_rate'],
                                         nation_location=cdh.display_covid['national_name'],
                                         national_7day_infections=
                                         cdh.display_covid['national_rate'],
                                         hospital_cases=cdh.display_covid['hospital_cases'],
                                         deaths_total=cdh.display_covid['total_deaths'],
                                         news_articles=cnh.display_news, updates=us.schedules,
                                         image='dashboard.png', title='Coronavirus Data',
                                         favicon='/static/images/favicon.ico')


@app.route('/')
def start():
    """Redirects website to '/index' from '/'.

       :return: A redirect to the home page
       :rtype: flask redirect function
    """
    return redirect(url_for('home'))


def config_load():
    """Loads the config file and iterates through it, adding its events to the scheduler."""
    config_dict = ch.json_load()

    logging.info("config file loaded")
    logging.debug("config after read: %s", config_dict)
    for i in config_dict['schedules']:  # loads schedules from config file
        try:  # creates schedules with time, name, repeat and category arguments
            cdh.schedule_covid_updates(i['content'][3:], i['name'], i['repeat'], i['category'])
        except ValueError:
            logging.exception("Exception when trying to run schedule_covid_updates")
