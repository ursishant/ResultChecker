from result_status import get_status_display

def test_result_status_declared():
    course = {
        "result_declared": True,
        "result_date": "2024-01-01",
        "official_result_url": "https://example.com"
    }
    
    status, date, url = get_status_display(course)
    assert status == "Result Declared"
    assert date == "2024-01-01"
    assert url == "https://example.com"

def test_result_status_not_declared():
    course = {
        "result_declared": False,
        "result_date": None,
        "official_result_url": None
    }
    
    status, date, url = get_status_display(course)
    assert status == "Result Not Declared"
    assert date is None
    assert url is None

def test_result_status_none():
    status, date, url = get_status_display(None)
    assert status == "Unknown"
    assert date is None
    assert url is None
