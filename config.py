"""
Configuration file for the Phonebook Application
"""

# Application Settings
APP_TITLE = "Assistant Phonebook"
APP_WIDTH = 900
APP_HEIGHT = 800

# File Settings
CONTACTS_FILE = "contacts.json"
SETTINGS_FILE = "settings.json"
ENCODING = "utf-8"

# Default Birthday Notification Settings
DEFAULT_NOTIFICATION_DAYS = [0, 1, 3, 7]

# UI Settings
FONT_NORMAL = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")
FONT_SMALL = ("Arial", 8)

# Date Format
DATE_FORMAT = "YYYY-MM-DD"

# Messages
MESSAGES = {
    "validation_name_required": "Name is required!",
    "success_contact_added": "Contact added successfully!",
    "success_contact_updated": "Contact updated successfully!",
    "success_contact_deleted": "Contact deleted successfully!",
    "error_add_contact": "Failed to add contact!",
    "error_update_contact": "Failed to update contact!",
    "error_delete_contact": "Failed to delete contact!",
    "confirm_delete": "Are you sure you want to delete this contact?",
    "warning_no_contact": "No contact selected!",
}

# UI Labels
LABELS = {
    "search": "Search",
    "new_contact": "New Contact",
    "clear": "Clear",
    "contacts": "Contacts",
    "contact_details": "Contact Details",
    "name": "Name:",
    "phone1": "Phone 1:",
    "phone2": "Phone 2:",
    "email": "Email:",
    "birthday": "Birthday:",
    "tags": "Tags:",
    "note": "Note:",
    "save": "Save",
    "delete": "Delete",
    "clear_form": "Clear Form",
    "date_format_hint": "(YYYY-MM-DD)",
    "tags_hint": "(comma separated)",
}
