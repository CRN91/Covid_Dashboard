from dashboard.config_handler import json_load, json_write, json_create, config_update
from os import remove as os_remove

def test_json_load():
    assert json_load("test1.json") == {"test_key": "test_value"}

def test_json_load_type():
    assert isinstance(json_load("test1.json"), dict)

def test_json_write():
    data = {"test_key": "test_value"}
    json_write(data, "test2.json")
    assert json_load("test2.json") == data

def test_json_create():
    data = {'api_key': 'api_key',
            'schedules': [],
            'location': {'nation_name': None,
                         'nation_type': None,
                         'local_name': None,
                         'local_type': None
                         }
            }
    json_create(filename="test3.json")
    assert json_load(filename="test3.json") == data
    os_remove("test3.json")  # 'test3.json' must be removed so on reruns it can test properly

def test_config_update():
    config_update({"schedules": {"test_key": "test_value"}}, filename="test4.json")
