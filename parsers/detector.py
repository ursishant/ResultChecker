import fitz  # PyMuPDF
import io

def extract_text_from_pdf(pdf_source):
    """Extracts all text from a PDF. Accepts file path or bytes."""
    text = ""
    try:
        if isinstance(pdf_source, bytes):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        else:
            doc = fitz.open(pdf_source)
            
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")
    return text

def detect_format(pdf_source):
    """
    Detects whether the PDF is a candidate response sheet (DigiALM)
    or an official answer key, or unsupported.
    Returns: 'response_sheet', 'answer_key', or 'unsupported'
    """
    text = extract_text_from_pdf(pdf_source)
    text_lower = text.lower()
    
    # Heuristics for DigiALM response sheet
    if "question id" in text_lower and "chosen option" in text_lower and "status :" in text_lower:
        return 'response_sheet'
        
    # Heuristics for Official Answer Key
    if "question id" in text_lower and "correct option" in text_lower:
        return 'answer_key'
        
    return 'unsupported'
