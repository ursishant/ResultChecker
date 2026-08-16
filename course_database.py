import json
import os

class CourseDatabase:
    def __init__(self, data_path=None):
        if data_path is None:
            # Default to data/courses.json relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(base_dir, "data", "courses.json")
        else:
            self.data_path = data_path
        
        self.courses = []
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.courses = data.get("courses", [])
        except FileNotFoundError:
            # Log warning or handle silently depending on requirements.
            # In a real app we'd log this.
            self.courses = []
        except json.JSONDecodeError:
            self.courses = []

    def get_all_courses(self):
        return self.courses

    def search_courses(self, query):
        if not query:
            return self.courses
            
        query = query.lower()
        results = []
        for course in self.courses:
            name = course.get("name", "").lower()
            code = course.get("code", "").lower()
            if query in name or query in code:
                results.append(course)
        return results

    def get_course_by_code(self, code):
        for course in self.courses:
            if course.get("code") == code:
                return course
        return None
        
    def get_course_by_name(self, name):
        for course in self.courses:
            if course.get("name") == name:
                return course
        return None
