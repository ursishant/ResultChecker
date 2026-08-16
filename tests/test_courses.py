import pytest
from course_database import CourseDatabase
import tempfile
import json
import os

# --- Test 10: Course database ---
def test_course_database():
    mock_data = {
        "courses": [
            {
                "id": "c1",
                "code": "01",
                "name": "Math",
                "result_declared": True,
                "result_date": "2024-01-01"
            },
            {
                "id": "c2",
                "code": "02",
                "name": "Physics",
                "result_declared": False,
                "result_date": None
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump(mock_data, f)
        temp_name = f.name
        
    try:
        db = CourseDatabase(data_path=temp_name)
        
        c1 = db.get_course_by_code("01")
        assert c1["result_declared"] == True
        
        c2 = db.get_course_by_code("02")
        assert c2["result_declared"] == False
        
        search_res = db.search_courses("math")
        assert len(search_res) == 1
        assert search_res[0]["code"] == "01"
        
    finally:
        os.unlink(temp_name)
