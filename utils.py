"""
Utility functions for the Phonebook Application
"""

import re
from datetime import datetime

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone.strip():
        return True
    phone_pattern = r'^[\d\s\-\+\(\)]+$'
    return bool(re.match(phone_pattern, phone))

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email.strip():
        return True
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_birthday(birthday: str) -> bool:
    """Validate birthday format (YYYY-MM-DD)"""
    if not birthday.strip():
        return True
    try:
        datetime.strptime(birthday, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def format_phone(phone: str) -> str:
    """Format phone number for display"""
    if not phone.strip():
        return ""
    return phone.strip()

def get_age_from_birthday(birthday: str) -> int:
    """Calculate age from birthday"""
    if not birthday.strip():
        return None
    try:
        birth_date = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def is_birthday_today(birthday: str) -> bool:
    """Check if birthday is today"""
    if not birthday.strip():
        return False
    try:
        birth_date = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.today()
        return (birth_date.month == today.month and birth_date.day == today.day)
    except ValueError:
        return False

def truncate_text(text: str, length: int = 50) -> str:
    """Truncate text to specified length"""
    if len(text) > length:
        return text[:length-3] + "..."
    return text

def highlight_search_term(text: str, term: str) -> str:
    """Highlight search term in text (case-insensitive)"""
    if not term:
        return text
    replacement = f"\033[1;32m{term}\033[0m"
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return pattern.sub(lambda m: f"\033[1;32m{m.group(0)}\033[0m", text)
1