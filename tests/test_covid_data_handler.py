from pandas import DataFrame
from dashboard.covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request,\
    schedule_covid_updates, first_non_null, config_location

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_covid_API_request_dataframe():
    assert isinstance(covid_API_request(dictionary=False), DataFrame)

def test_first_non_null():
    assert first_non_null(['', 'test']) == 'test'

def test_first_non_null_none():
    assert first_non_null(['', '']) is None

def test_schedule_covid_updates_seconds():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_schedule_covid_updates_24_hour():
    schedule_covid_updates(update_interval='00:00', update_name='update test')

def test_config_location():
    assert isinstance(config_location(), dict)
