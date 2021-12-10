from dashboard.covid_news_handling import news_API_request, close_news

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_close_news():
    assert close_news('test_article', ['test']) == ['test', 'test_article']
