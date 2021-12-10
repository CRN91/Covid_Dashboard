"""This module was designed specifically to be used by a covid-19 dashboard application and
   contains functions to initiate and edit a scheduler from the sched module and it maintains a
   list named 'schedules' that contains dictionaries representing an event in the scheduler that
   can be used to update the ui and store in an external file.
"""
import typing
from sched import scheduler
import time
import logging
import dashboard.config_handler as ch

update_scheduler = scheduler(time.time, time.sleep)
schedules = []
DAY = 86400  # constant: seconds in one day


def difference_seconds(update_time: str) -> int:
    """Takes time in 24 hour format and returns the difference between then and local time.

       Calculates the difference in time between the users local time and the update_time in
       seconds. If the value is negative 86400 seconds (representing one day) is added to the result
       before it is returned.

       :parameter update_time: Time to be calculated against, 24 hour format separated by a colon
       :type update_time: str

       :return: The time in seconds until the next update
       :rtype: int
    """
    logging.info("starting difference_seconds function")
    if update_time == '':  # if no time is submitted then the updates are run immediately
        logging.warning("No user time for the scheduled update, will assume current time")
        return 0

    interval_split = update_time.split(':')
    time_now_split = str(time.strftime("%H:%M:%S")).split(":")  # gets local time
    logging.debug('user requested time: %s', interval_split)
    logging.debug('current time: %s', time_now_split)

    time_seconds = ((int(interval_split[0]) - int(time_now_split[0]))*3600
                    + (int(interval_split[1]) - int(time_now_split[1]))*60)\
                    - int(time_now_split[2])  # calculates time in seconds between local time and
                                              # scheduled time
    if time_seconds < 0:
        time_seconds += DAY  # time can't be negative, so moves over to next day
    logging.debug('schedule set to update in %s seconds', time_seconds)
    return time_seconds


def unique_name(initial: str, category: str) -> str:
    """Takes name and category and returns a unique schedule name comparing against schedules list.

       Creates a unique name for the scheduler by adding a number to the end of the string,
       if a unique name cannot be found after 128 attempts the schedule will not be made as
       to not get stuck in a time consuming loop.

       :parameter initial: The name to be checked if unique
       :type initial: str
       :parameter category: The category of the update, currently only accepts 'covid' or 'news'
       :type category: str

       :return: Display name for the scheduler
       :rtype: str
    """
    unique = False
    schedule_titles = []
    for i in schedules:  # names must be unique as html returns a string of the name
        schedule_titles.append(i['title'])
    logging.debug("schedule titles = %s", schedule_titles)
    name = initial
    for j in range(1, 129):  # if a name can't be made after 128 attempts there's probably an error
        if not check_unique(category+' update: '+name, schedule_titles):
            logging.error("User has entered a non-unique name: %s", initial)
            name = initial+'('+str(j)+')'  # adds (x) to end of name if its not unique
        else:                              # with x being a natural number between 1 and 128
            unique = True
            break  # if its unique it breaks out of the loop
    if not unique:  # if a unique name can't be found the scheduled event is cancelled
        logging.error("A unique name cannot be made in a reasonable amount of tries")
        logging.warning("The schedule update label must be unique, cancelling request")
        name = None
    return category+' update: '+name, name  # first value is in the format for the ui


def check_unique(item, array: list) -> bool:
    """Returns True if an item is not in a list

       :parameter item: Checks item against a list
       :type item: any
       :parameter array: List to be checked against
       :type array: list

       :return: True if an item is not in a list
       :rtype: bool
       """
    return not item in array


def close_schedule(sched_title: str):
    """Takes a title and removes its corresponding event from schedules and the scheduler.

       :parameter sched_title: The title of the event requested to be removed
       :type sched_title: str
    """
    logging.debug('user request remove schedule data %s', sched_title)
    logging.info("user request to remove scheduled update")
    logging.debug("s.queue before removal = %s", update_scheduler.queue)
    for i in schedules:
        if sched_title == i['title']:
            schedules.remove(i)  # removes it from the list with dictionaries representing events
            for event in update_scheduler.queue:
                if sched_title == event[3][0]:
                    update_scheduler.cancel(event)  # cancels the event in the scheduler
                    logging.info("removed event from schedule queue")
                    logging.debug("s.queue after removal = %s", update_scheduler.queue)
                    ch.config_update(schedules)  # config is updated with new schedules list


def process_event(function: typing.Callable, name: str = None, repeat: bool = None,
                  blacklist_news: list = None):
    """Takes parameters for a schedule event and either removes it or repeats it for the next day

       If a schedule has been set to repeat, its data is left in the 'schedules' list and a new
       event set 24 hours from now is created in the scheduler. If the event is not set to repeat
       the event is removed from 'schedules' and no new event is created.

       :parameter function: The function to be run by the scheduler when the event is set to run
       :type function: function
       :parameter name: The title of the scheduler event
       :type name: str, optional
       :parameter repeat: The value associated with whether an event needs to repeat
       :type repeat: bool, optional
       :parameter blacklist_news: A list of news article titles that have been blacklisted
       :type blacklist_news: list
    """
    logging.info("starting process_event procedure")
    if name:
        for i in schedules:
            logging.debug("schedule = %s", i)
            if i['title'] == name:
                if i['repeat']:  # creates a new event in scheduler if its set to repeat
                    if str(function) == "update_covid":
                        update_scheduler.enter(DAY, 1, function, (name, repeat))
                    elif str(function) == "update_news":
                        update_scheduler.enter(DAY, 1, function, (blacklist_news, name, repeat))
                else:  # removes it from schedules, already removed from scheduler when it was run
                    logging.info('removed: %s from schedules', i)
                    schedules.remove(i)

        ch.config_update(schedules)  # updates config with latest version of schedules
