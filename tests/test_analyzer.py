import pytest
from analyzer import analyze_answers

# Mock Response Sheet Data
def get_response_data():
    return [
        {
            "question_id": "Q001",
            "chosen_option": 2,
            "status": "Answered",
            "option_ids": {1: "O001", 2: "O002", 3: "O003", 4: "O004"}
        },
        {
            "question_id": "Q002",
            "chosen_option": 3,
            "status": "Answered",
            "option_ids": {1: "O011", 2: "O012", 3: "O013", 4: "O014"}
        },
        {
            "question_id": "Q003",
            "chosen_option": None,
            "status": "Not Answered",
            "option_ids": {1: "O021", 2: "O022", 3: "O023", 4: "O024"}
        }
    ]

# Mock Answer Key Data
def get_answer_key():
    return {
        "Q001": "O002", # Test 1: Correct (matches chosen option 2)
        "Q002": "O011", # Test 2: Incorrect (chosen option 3 = O013 != O011)
        "Q003": "O022", # Test 3: Unattempted
        "Q004": "O031"  # Test 4: Missing (in key but not in response)
    }

def test_analyzer_scenarios():
    df, stats = analyze_answers(get_response_data(), get_answer_key())
    
    # Check stats
    assert stats["correct"] == 1
    assert stats["incorrect"] == 1
    assert stats["unattempted"] == 1
    assert stats["missing"] == 1
    assert stats["attempted"] == 2
    assert stats["accuracy"] == 50.0  # 1/2 * 100
    assert stats["estimated_score"] == 2 # 1 correct * 2 + 1 incorrect * 0
    
    # Check individual results
    res_q1 = df[df["Question ID"] == "Q001"].iloc[0]["Result"]
    assert res_q1 == "Correct"
    
    res_q2 = df[df["Question ID"] == "Q002"].iloc[0]["Result"]
    assert res_q2 == "Incorrect"
    
    res_q3 = df[df["Question ID"] == "Q003"].iloc[0]["Result"]
    assert res_q3 == "Unattempted"
    
    res_q4 = df[df["Question ID"] == "Q004"].iloc[0]["Result"]
    assert res_q4 == "Missing"

# --- Test 5: Question order ---
def test_question_order():
    resp_data = [
        {
            "question_id": "Q003",
            "chosen_option": 1,
            "status": "Answered",
            "option_ids": {1: "O001"}
        },
        {
            "question_id": "Q001",
            "chosen_option": 1,
            "status": "Answered",
            "option_ids": {1: "O002"}
        },
        {
            "question_id": "Q002",
            "chosen_option": 1,
            "status": "Answered",
            "option_ids": {1: "O003"}
        }
    ]
    
    key_data = {
        "Q001": "O002",
        "Q002": "O003",
        "Q003": "O001"
    }
    
    df, stats = analyze_answers(resp_data, key_data)
    
    assert stats["correct"] == 3
    assert stats["matched_percentage"] == 100.0
