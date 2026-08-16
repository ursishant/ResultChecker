def get_status_display(course):
    """Returns the formatted status display for a course."""
    if not course:
        return "Unknown", None, None
        
    is_declared = course.get("result_declared", False)
    date = course.get("result_date")
    url = course.get("official_result_url")
    
    if is_declared:
        return "Result Declared", date, url
    return "Result Not Declared", None, None
