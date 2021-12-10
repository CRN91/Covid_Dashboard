"""This is the main file of the covid dashboard and simply runs the setup of the logger, the setup
   of the application and then the application.
"""
import dashboard.dashboard_ui as ui
import dashboard.custom_logger as cl

if __name__ == "__main__":
    cl.logger_setup()
    ui.setup()
    ui.app.run()  # argument debug=True allows for debugging
