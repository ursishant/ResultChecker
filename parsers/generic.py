import re
from .detector import extract_text_from_pdf

def parse_answer_key(pdf_file_path):
    text = extract_text_from_pdf(pdf_file_path)
    
    questions = {}
    
    # The official answer key typically is a table with rows.
    # Usually we can find pairs of Question ID and Correct Option ID.
    # The challenge is they might be separated by spaces or newlines.
    
    # Try to find all numeric blocks that look like IDs.
    # In UGC NET, Question IDs and Option IDs are long numbers (e.g., 10 digits).
    # But let's look for explicit "Question ID" and "Correct Option ID" headers if they exist,
    # or just match pairs of large numbers.
    
    # A common format is a table with columns: S.No, Question ID, Correct Option ID
    # Since PyMuPDF extracts text left-to-right, top-to-bottom, we often get:
    # 1
    # 1234567890
    # 1234567892
    
    # Let's try to match lines that contain 2 large numbers.
    # Or, we can use a regex to find all large numbers (length > 5).
    # This might be tricky. Let's make it more robust.
    
    lines = text.split('\n')
    
    # Clean up lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Strategy 1: Look for rows where Question ID and Correct Option are in the same line
    # (e.g. if extracted as "1234567890 1234567892")
    pair_pattern = re.compile(r"(\d{5,})\s+(\d{5,})")
    
    found_pairs = False
    for line in lines:
        matches = pair_pattern.findall(line)
        for m in matches:
            qid, ans_id = m[0], m[1]
            questions[qid] = ans_id
            found_pairs = True
            
    if found_pairs and len(questions) > 10:
        return questions
        
    # Strategy 2: In PyMuPDF, table cells often end up on separate lines.
    # If we see a sequence of numbers, the sequence might be:
    # S.No, Question ID, Correct Option ID.
    # Let's collect all large numbers (assumed to be IDs).
    
    large_numbers = []
    for line in lines:
        if line.isdigit() and len(line) >= 5:
            large_numbers.append(line)
            
    # Since QID and AnsID come in pairs, the list of large numbers
    # might alternate: QID, AnsID, QID, AnsID...
    # Let's check if the list length is even.
    # If not, maybe there are headers mixed in.
    
    if len(large_numbers) > 0 and len(large_numbers) % 2 == 0:
        for i in range(0, len(large_numbers), 2):
            questions[large_numbers[i]] = large_numbers[i+1]
            
    if not questions:
        raise ValueError("Could not extract Question IDs and Correct Option IDs from the answer key.")
        
    return questions
