from datetime import datetime

def normalize_date(date_str: str) -> str:
    """
    Normalizes a date string to DD-MM-YYYY format.
    Handles:
    - ISO format with time (YYYY-MM-DDTHH:MM:SS.sssZ)
    - Simple ISO date (YYYY-MM-DD)
    - Existing DD-MM-YYYY
    """
    # If it contains 'T', we assume it's an ISO-like string and take the date part
    clean_date_str = date_str.split('T')[0]

    try:
        # Try parsing as ISO (YYYY-MM-DD)
        dt = datetime.strptime(clean_date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except ValueError:
        pass

    try:
        # Check if it's already DD-MM-YYYY
        datetime.strptime(clean_date_str, "%d-%m-%Y")
        return clean_date_str
    except ValueError:
        pass
    
    # Return original if we can't parse it
    return date_str
