import pandas as pd
import io

def generate_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def generate_excel(df, stats, course_name, result_status):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_data = {
            "Metric": [
                "Selected Course",
                "Result Status",
                "Total Questions",
                "Attempted",
                "Correct",
                "Incorrect",
                "Unattempted",
                "Missing",
                "Accuracy",
                "Correct Marks",
                "Negative Marks",
                "Estimated Score"
            ],
            "Value": [
                course_name,
                result_status,
                stats.get("total_key_questions", 0),
                stats.get("attempted", 0),
                stats.get("correct", 0),
                stats.get("incorrect", 0),
                stats.get("unattempted", 0),
                stats.get("missing", 0),
                f"{stats.get('accuracy', 0)}%",
                stats.get("correct", 0) * 2, # Defaults used if actual unknown here, but UI should pass
                stats.get("incorrect", 0) * 0,
                stats.get("estimated_score", 0)
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
        
        # Sheet 2: All Questions
        df.to_excel(writer, sheet_name="All Questions", index=False)
        
        # Sheet 3: Correct
        df[df["Result"] == "Correct"].to_excel(writer, sheet_name="Correct", index=False)
        
        # Sheet 4: Incorrect
        df[df["Result"] == "Incorrect"].to_excel(writer, sheet_name="Incorrect", index=False)
        
        # Sheet 5: Unattempted
        df[df["Result"] == "Unattempted"].to_excel(writer, sheet_name="Unattempted", index=False)
        
        # Sheet 6: Missing
        df[df["Result"] == "Missing"].to_excel(writer, sheet_name="Missing", index=False)
        
    return output.getvalue()
