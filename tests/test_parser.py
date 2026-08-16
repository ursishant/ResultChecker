import pytest
from unittest.mock import patch
from parsers import detect_format, parse_response_sheet, parse_answer_key

# --- Test 7: Duplicate Question ID ---
@patch('parsers.detector.extract_text_from_pdf')
def test_duplicate_question_id(mock_extract):
    mock_extract.return_value = """
    Question ID : 11111
    Option 1 ID : 1
    Option 2 ID : 2
    Status : Answered
    Chosen Option : 1
    
    Question ID : 11111
    Option 1 ID : 1
    Status : Answered
    Chosen Option : 1
    """
    with pytest.raises(ValueError, match="Duplicate Question IDs detected"):
        parse_response_sheet(b"dummy_bytes")

# --- Test 8: Invalid PDF ---
def test_invalid_pdf():
    # Invalid bytes
    with pytest.raises(ValueError):
        detect_format(b"not a pdf")

# --- Test 9: Unsupported format ---
@patch('parsers.detector.extract_text_from_pdf')
def test_unsupported_format(mock_extract):
    mock_extract.return_value = "This is a random text with no known format."
    assert detect_format(b"dummy_bytes") == 'unsupported'
    
@patch('parsers.detector.extract_text_from_pdf')
def test_detect_digialm(mock_extract):
    mock_extract.return_value = "Question ID : 123 Status : Answered Chosen Option : 1"
    assert detect_format(b"dummy_bytes") == 'response_sheet'

# --- Test 6: Option mapping ---
@patch('parsers.detector.extract_text_from_pdf')
def test_option_mapping(mock_extract):
    mock_extract.return_value = """
    Question ID : 999
    Option 1 ID : 101
    Option 2 ID : 102
    Option 3 ID : 103
    Option 4 ID : 104
    Status : Answered
    Chosen Option : 3
    """
    res = parse_response_sheet(b"dummy_bytes")
    assert len(res) == 1
    assert res[0]['question_id'] == "999"
    assert res[0]['chosen_option'] == 3
    assert res[0]['option_ids'][3] == "103"
