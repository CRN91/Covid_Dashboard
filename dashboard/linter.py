import pylint.lint
pylint_opts = ['config_handler.py', 'covid_data_handler.py', 'dashboard_ui.py',
               'covid_news_handling.py', 'main.py', 'scheduler_updater.py',
               'custom_logger.py'
               ]
pylint.lint.Run(pylint_opts)
