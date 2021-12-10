"""This module was designed specifically to be used by a covid-19 dashboard application and
   contains functions to create, load and write to 'config.json' file.

   The functions:

   - json_write
   - json_load

   can be used to write a payload or load any json file, just specify filename='your_file.json' and
   your payload (if applicable).
   """
import json
import logging
from os import path


def json_write(payload: dict, filename: str = 'config.json'):
    """Takes a payload and filename and writes the payload to the file.

       :parameter payload: Dictionary to be writen to json file
       :type payload: dict
       :parameter filename: Filename of json file to be written to, default file is 'config.json'
       :type filename: str, optional
    """
    logging.info("writing to json file")
    logging.debug("to be written to json file: %s", payload)
    with open(filename, "w", encoding='utf-8') as outfile:
        json.dump(payload, outfile)


def json_load(filename: str = 'config.json') -> dict:
    """Takes filename of a json file and returns the data it reads from it.

       :parameter filename: Filename of json file to be read, default file is 'config.json'
       :type filename: str, optional

       :return: The dictionary loaded from the json file
       :rtype: dict
    """
    logging.info("loading json file")
    with open(filename, "r", encoding='utf-8') as json_data_file:
        logging.info("json file loaded")
        return json.load(json_data_file)


def json_create(overwrite: bool = False, filename='config.json'):  # creates json file if none found
    """Takes a boolean, then creates a config if not found or overwrite = True.

       :parameter overwrite: If set to true it will overwrite the config file even if one is found
       :type overwrite: bool, optional
    """
    logging.info("setting up config file")
    config_file = {'api_key': 'api_key',  # enter your api key here as a string or
                                          # manually into config.json
                   'schedules': [],
                   'location': {'nation_name': None,  # enter your location data here according to
                                'nation_type': None,  # https://coronavirus.data.gov.uk
                                'local_name': None,   # /details/developers-guide
                                'local_type': None    # or manually into config.json
                                }
                   }
    if not path.exists(filename) or overwrite:
        json_write(config_file, filename=filename)


def config_update(schedules: list, filename='config.json'):
    """Takes schedules and overwrites schedules in the config file with the new schedules.

       :parameter schedules: List of dictionaries each representing an event in the scheduler
       :type schedules: list
    """
    logging.info("updating config")
    config_dict = json_load(filename)  # load old config
    config_dict['schedules'] = schedules  # updated dictionary to be written
    logging.debug("updated config before writing to file: %s", config_dict)
    json_write(config_dict, filename)  # writes updated dictionary
