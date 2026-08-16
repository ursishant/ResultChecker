def bytes_to_mb(size_in_bytes):
    return size_in_bytes / (1024 * 1024)

def is_valid_pdf_size(file_bytes, max_mb=20):
    return bytes_to_mb(len(file_bytes)) <= max_mb
