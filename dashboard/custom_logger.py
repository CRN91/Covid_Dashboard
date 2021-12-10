"""This module creates two loggers from the logging module, one is a console logger that logs all
   debug level logs and a file logger that logs all info level logs to 'sys.log'.
"""
import logging
from logging import config

def logger_setup(console_level: int=logging.DEBUG, file_level: int=logging.INFO,
                 filename: str='sys.log') -> str:
    """Creates 2 loggers, a console debug logger and a file info logger that writes to 'sys.log'.

       Creates 2 loggers, a debug level logger that prints to the console and an info level
       logger that prints to the file sys.log. The console logger is formatted to print the line
       number, the file it was run in and the message. The file logger is formatted to print;
       the logger level, the time in the format: 'Year:Month:Day Hour:Minute:Second:millisecond',
       the function, file and line it was run at and the message.

       The level of the loggers and the file that is written to can be changed with the parameters.

       :parameter console_level: logging module level to be written to console,
                                 default = logging.DEBUG == 10
       :type console_level: int, optional
       :parameter file_level: logging module level to be written to file,
                              default = logging.INFO == 20
       :type file_level: int, optional
       :parameter filename: Name of the file for the file logger to write to, default = 'sys.log'
       :type filename: str, optional
    """
    config.dictConfig({'version': 1,  # does nothing, its for future compatibility
                       'formatters': {'info': {'format': "%(levelname)s at %(asctime)s in "
                                                         "%(funcName)s in %(filename) at line"
                                                         "%(lineno)d: %(message)s"
                                               },
                                      'debug': {'format': "%(lineno)d in %(filename)s: %(message)s"}
                                      },
                       'handlers': {'console': {'class': 'logging.StreamHandler',  # console logger
                                                'formatter': 'debug',
                                                'level': console_level
                                                },
                                    'file': {'class': 'logging.FileHandler',  # file logger
                                             'filename': filename,
                                             'formatter': 'info',
                                             'encoding': 'utf-8',
                                             'mode': 'w',  # truncates file
                                             'level': file_level
                                             }
                                    },
                       'root': {'handlers': ('console', 'file'),
                                'level': logging.NOTSET  # other handlers inherit this level so
                                }                        # must be set to NOTSET
                       })

    logging.info("Logger setup to sys.log and console")
