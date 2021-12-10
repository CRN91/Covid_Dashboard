from dashboard.scheduler_updater import difference_seconds, unique_name, check_unique

def test_difference_seconds_0():
    assert difference_seconds('') == 0

def test_difference_seconds():
    assert isinstance(difference_seconds('00:00'), int)

def test_unique_name():
    assert unique_name('test_name', 'test_category') ==\
           ('test_category update: test_name', 'test_name')

def test_check_unique_non_unique():
    assert check_unique('test', ['test']) is False

def test_check_unique_unique():
    assert check_unique('test', []) is True
