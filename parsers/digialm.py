import re
from .detector import extract_text_from_pdf

def parse_response_sheet(pdf_file_path):
    text = extract_text_from_pdf(pdf_file_path)
    
    questions = []
    
    # We will find all relevant fields and their positions in the text.
    # This approach is resilient to changes in ordering.
    
    qid_pattern = re.compile(r"Question\s*ID\s*[:\-]\s*(\d+)", re.IGNORECASE)
    opt1_pattern = re.compile(r"Option\s*1\s*ID\s*[:\-]\s*(\d+)", re.IGNORECASE)
    opt2_pattern = re.compile(r"Option\s*2\s*ID\s*[:\-]\s*(\d+)", re.IGNORECASE)
    opt3_pattern = re.compile(r"Option\s*3\s*ID\s*[:\-]\s*(\d+)", re.IGNORECASE)
    opt4_pattern = re.compile(r"Option\s*4\s*ID\s*[:\-]\s*(\d+)", re.IGNORECASE)
    status_pattern = re.compile(r"Status\s*[:\-]\s*([A-Za-z\s]+)", re.IGNORECASE)
    chosen_pattern = re.compile(r"Chosen\s*Option\s*[:\-]\s*(\d+|--)", re.IGNORECASE)
    
    # Find all Question IDs
    qids = []
    for m in qid_pattern.finditer(text):
        qids.append({'id': m.group(1), 'start': m.start(), 'end': m.end()})
        
    if not qids:
        raise ValueError("No Question IDs found in the response sheet.")
        
    # Check for duplicate Question IDs (rare but possible if PDF is weird)
    seen_qids = set()
    for q in qids:
        if q['id'] in seen_qids:
            raise ValueError(f"Duplicate Question IDs detected: {q['id']}. The document may not be in a supported format.")
        seen_qids.add(q['id'])
        
    # Now, for each Question ID, the relevant fields are typically between its start
    # and the start of the next Question ID.
    for i in range(len(qids)):
        q_start = qids[i]['start']
        q_end = qids[i+1]['start'] if i + 1 < len(qids) else len(text)
        
        block = text[q_start:q_end]
        
        o1 = opt1_pattern.search(block)
        o2 = opt2_pattern.search(block)
        o3 = opt3_pattern.search(block)
        o4 = opt4_pattern.search(block)
        status_match = status_pattern.search(block)
        chosen_match = chosen_pattern.search(block)
        
        status = status_match.group(1).strip() if status_match else "Unknown"
        
        # Clean status line breaks
        status = re.sub(r'\s+', ' ', status)
        
        chosen = None
        if chosen_match:
            c_val = chosen_match.group(1).strip()
            if c_val.isdigit():
                chosen = int(c_val)
                
        questions.append({
            "question_id": qids[i]['id'],
            "status": status,
            "chosen_option": chosen,
            "option_ids": {
                1: o1.group(1) if o1 else None,
                2: o2.group(1) if o2 else None,
                3: o3.group(1) if o3 else None,
                4: o4.group(1) if o4 else None,
            }
        })
        
    return questions
