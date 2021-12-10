"""This module was designed specifically to be used by a covid-19 dashboard application and
   contains functions to request news articles from newsapi, process them, send them to the UI and
   remove articles as per user request.

   The function news_API_request can be used to request news articles about any topic by sending
   a custom argument as covid_terms and the country and language can be changed with their
   parameters of the same name. However the function will make the title of each article a
   hyperlink and will try to fill the 'content' value of each article with its description if
   available.
"""
import logging
import typing
import flask
from newsapi import NewsApiClient, newsapi_exception
from requests.exceptions import ConnectionError as requestsConnectionError
import dashboard.config_handler as ch
import dashboard.scheduler_updater as us

all_news = []
display_news = []


def news_API_request(covid_terms: str = 'Covid COVID-19 coronavirus', country: str = 'gb',
                     language: str = 'en') -> list:
    """Takes a string of covid terms and returns a list of top headlines as requested from newsapi.

       Makes a request to newsapi for the top headlines relating to the keywords in
       covid_terms and returns a list of articles represented as dictionaries after
       removing duplicates from the request.

       :parameter covid_terms: search terms separated by a blank space
       :type covid_terms: str
       :parameter country: country that the news is taken from, default is the United Kingdom
       :type country: str, optional
       :parameter language: language that the news is taken from, default is the english
       :type language: str, optional

       :return: A list of dictionaries, each dict representing a news article
       :rtype: list
    """
    logging.info("starting news_API_request function")
    api_key = ch.json_load()['api_key']
    newsapi = NewsApiClient(api_key=api_key)  # initialises newsapi

    # Requests links for top headlines related to search terms
    top_headlines_request = []
    for i in covid_terms.split():
        try:
            top_headlines_request.append(newsapi.get_top_headlines(q=i,
                                                                   country=country,
                                                                   language=language
                                                                   ))
        except newsapi_exception.NewsAPIException:  # newsapi returned error
            logging.exception("newsapi has returned an exception to the request")
            return [{'title': 'Error', 'content': 'newsapi has returned an error'}]
        except requestsConnectionError:  # couldn't connect to newsapi
            logging.exception("Connection Error when connecting to newsapi")
            return [{'title': 'Error', 'content': "Can't connect to newspai"}]
        logging.debug(top_headlines_request)

    top_headlines = []
    for j in top_headlines_request:
        headlines = j['articles']
        for article in headlines:
            article['title'] = flask.Markup(f'<a href={article["url"]} target=_blank rel='
                                            f'noopener noreferrer>{article["title"]}</a>')
            # creates a hyperlink for the news title, target=_blank opens the page in a new tab
            #  and rel=noopener noreferrer is a common security patch
            if article['description'] and article['description'] != '':
                article['content'] = article['description']  # tries to make the description the
        top_headlines += headlines                           # content as it is more suited to the
                                                             # app and specification states the
    logging.info("news_API_request function finished")       # html can't be edited
    return [i for n, i in enumerate(top_headlines) if i not in top_headlines[n + 1:]]
    # removes duplicate articles


def close_news(news_title: str, blacklist: list) -> list:
    """Takes a news title and blacklist, removes the news from displaying and adds it to blacklist.

       :parameter news_title: Title of a news article that is to be removed
       :type news_title: str
       :parameter blacklist: A list of news article titles that have been blacklisted
       :type blacklist: list

       :return: The updated blacklist
       :rtype: list
    """
    logging.debug('user request remove schedule data %s', news_title)
    logging.info("user request to remove news article")
    logging.debug("display_news = %s", display_news)
    logging.debug("blacklist = %s", blacklist)

    # removes article from display_news
    for article in display_news:
        if news_title == article['title']:
            display_news.remove(article)

    blacklist.append(news_title)  # adds the article to the blacklist so it doesn't reappear
    set_display(blacklist)  # calls for set_display to replenish display_news if possible
    return blacklist  # returns updated blacklist, not sent to config in case user
                      # accidently deletes an article they can just request another news update


def update_news(blacklist: list, event_title: typing.Optional[str] = None,
                repeat: typing.Optional[bool] = None):
    """Calls for news articles and creates a list of 4 articles to be displayed on the dashboard.

       Makes a new request for news articles from news_API_requests and overwrites set_display to
       contain four news articles that are to be used by flask when rendering the dashboard. This
       function, update_news, can be called in two places, either on its own to run an update or by
       the sched module's scheduler. When called by the scheduler the parameters 'event_title' and
       'repeat' of the event that called it are needed so the event can be removed from the
       scheduler or repeated for the next day. 'display_news' is made to be a global variable as the
       sched module can not store anything that is returned when it runs its event's functions so to
       access the news you must import 'display_news'.

       :parameter blacklist: A list of news article titles that have been blacklisted
       :type blacklist: list
       :parameter event_title: The title of the scheduler event
       :type event_title: str, optional
       :parameter repeat: The value associated with whether an event needs to repeat
       :type repeat: bool, optional
    """
    logging.info("starting update_news procedure")

    global display_news  # must be global as sched module's scheduler can't return
    global all_news      # ditto

    all_news = news_API_request()
    try:
        display_news = all_news[0:4]  # 4 articles is a design choice to not overload the screen
        del all_news[:4]
    except IndexError:  # if all_news returns less than 4 articles
        logging.exception("IndexError all_news length was less than 4 articles")
        display_news = all_news  # fills display_news with everything as its less than 4
    logging.debug("display_news after update = %s", display_news)
    set_display(blacklist)

    if event_title: # if update_covid is called through the scheduler the event is to be processed
        us.process_event(update_news, event_title, repeat, blacklist_news=blacklist)


def set_display(blacklist: list):
    """Requests new news articles and updates the display with them.

       If there are spaces in display_news, such as after an article has been removed from the
       dashboard, articles are moved from all_news into display_news (if available) to fill the
       gaps. The articles in display_news are compared against a blacklist to remove news articles
       that the user has requested to be removed from their feed if they are placed back into
       display_news.

       :parameter blacklist: A list of news article titles that have been blacklisted
       :type blacklist: list
    """
    logging.info("starting set_display procedure")
    logging.debug("blacklisted articles = %s", blacklist)
    global display_news  # must be global as sched module's scheduler can't return

    logging.debug("length of display_news = %s", len(display_news))
    display_news_len = len(display_news)
    while display_news_len < 4:
        logging.debug("inside loop")
        if not all_news:  # breaks out of loop if there are no items to add from all_news
            logging.debug("all_news empty: %s", all_news)
            break
        display_news += all_news[:4 - display_news_len]  # adds news articles to fill in gaps
        logging.debug("display news has been lengthened to %s", len(display_news))
        del all_news[:4 - display_news_len]  # deletes the used articles from all_news

        # removes articles from display_news if they're found in blacklist
        match_case = set(i['title'] for i in display_news) & set(blacklist)  # set containing items
        logging.debug('match case = %s', match_case)                         # in both display_news
        for article in display_news:                                         # and blacklist
            if article['title'] in match_case:
                logging.debug("removing %s from %s", article, display_news)
                display_news.remove(article)

        display_news_len = len(display_news)        # can't use len() in while loop to allow the
    logging.info("set_display procedure finished")  # blacklist to be checked
