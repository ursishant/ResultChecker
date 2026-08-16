import pandas as pd

def analyze_answers(response_sheet_data, answer_key_data, marking_scheme=None):
    if marking_scheme is None:
        marking_scheme = {"correct": 2, "incorrect": 0, "unattempted": 0}
        
    results = []
    
    total_key_questions = len(response_sheet_data)
    
    # Track which questions from the answer key have been found
    found_key_questions = set()
    
    stats = {
        "total_key_questions": total_key_questions,
        "response_sheet_questions": len(response_sheet_data),
        "attempted": 0,
        "correct": 0,
        "incorrect": 0,
        "unattempted": 0,
        "missing": 0,
        "accuracy": 0.0,
        "estimated_score": 0
    }
    
    for i, q in enumerate(response_sheet_data, 1):
        qid = q["question_id"]
        chosen_option_num = q["chosen_option"]
        status = q["status"]
        option_ids = q["option_ids"]
        
        row = {
            "S.No": i,
            "Question ID": qid,
            "Chosen Option": chosen_option_num,
            "Chosen Option ID": None,
            "Correct Option ID": None,
            "Result": "Unknown"
        }
        
        # Determine candidate's chosen option ID
        if chosen_option_num and chosen_option_num in option_ids:
            row["Chosen Option ID"] = option_ids[chosen_option_num]
            
        # Match with answer key
        if qid in answer_key_data:
            found_key_questions.add(qid)
            correct_opt_id = answer_key_data[qid]
            row["Correct Option ID"] = correct_opt_id
            
            # Determine result
            if row["Chosen Option ID"] is None:
                row["Result"] = "Unattempted"
                stats["unattempted"] += 1
            elif str(row["Chosen Option ID"]) == str(correct_opt_id):
                row["Result"] = "Correct"
                stats["correct"] += 1
                stats["attempted"] += 1
            else:
                row["Result"] = "Incorrect"
                stats["incorrect"] += 1
                stats["attempted"] += 1
        else:
            # Question from response sheet not found in answer key
            row["Result"] = "Missing from Key"
            
        results.append(row)

        
    # Calculate Accuracy
    if stats["attempted"] > 0:
        stats["accuracy"] = round((stats["correct"] / stats["attempted"]) * 100, 2)
        
    # Calculate Score
    stats["estimated_score"] = (stats["correct"] * marking_scheme["correct"]) + \
                               (stats["incorrect"] * marking_scheme["incorrect"]) + \
                               (stats["unattempted"] * marking_scheme["unattempted"])
                               
    stats["matched_percentage"] = 0
    if total_key_questions > 0:
        stats["matched_percentage"] = round((len(found_key_questions) / total_key_questions) * 100, 2)
        
    df = pd.DataFrame(results)
    return df, stats
