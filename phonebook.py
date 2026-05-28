import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Phonebook:
    def __init__(self, filename: str = "contacts.json"):
        self.filename = filename
        self.contacts: List[Dict] = []
        self.load_contacts()

    def load_contacts(self):
        """Load contacts from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.contacts = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.contacts = []
        else:
            self.contacts = []

    def save_contacts(self):
        """Save contacts to JSON file immediately"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving contacts: {e}")
            return False

    def add_contact(self, name: str, phone1: str, phone2: str, email: str,
                   birthday: str, note: str, tags: List[str]) -> bool:
        """Add a new contact"""
        if not name.strip():
            return False

        contact = {
            "id": self._generate_id(),
            "name": name.strip(),
            "phone1": phone1.strip(),
            "phone2": phone2.strip(),
            "email": email.strip(),
            "birthday": birthday.strip(),
            "note": note.strip(),
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "created": datetime.now().isoformat()
        }
        self.contacts.append(contact)
        return self.save_contacts()

    def update_contact(self, contact_id: str, name: str, phone1: str, phone2: str,
                      email: str, birthday: str, note: str, tags: List[str]) -> bool:
        """Update an existing contact"""
        for contact in self.contacts:
            if contact["id"] == contact_id:
                contact.update({
                    "name": name.strip(),
                    "phone1": phone1.strip(),
                    "phone2": phone2.strip(),
                    "email": email.strip(),
                    "birthday": birthday.strip(),
                    "note": note.strip(),
                    "tags": [tag.strip() for tag in tags if tag.strip()],
                    "modified": datetime.now().isoformat()
                })
                return self.save_contacts()
        return False

    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        self.contacts = [c for c in self.contacts if c["id"] != contact_id]
        return self.save_contacts()

    def search_contacts(self, query: str) -> List[Dict]:
        """Search contacts by name, phone, email, or tags"""
        query = query.lower().strip()
        if not query:
            return self.contacts

        results = []
        for contact in self.contacts:
            if (query in contact["name"].lower() or
                query in contact["phone1"].lower() or
                query in contact["phone2"].lower() or
                query in contact["email"].lower() or
                any(query in tag.lower() for tag in contact["tags"])):
                results.append(contact)
        return results

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """Get a specific contact by ID"""
        for contact in self.contacts:
            if contact["id"] == contact_id:
                return contact
        return None

    def _generate_id(self) -> str:
        """Generate unique contact ID"""
        import uuid
        return str(uuid.uuid4())

    def get_all_tags(self) -> List[str]:
        """Get all unique tags from all contacts"""
        tags = set()
        for contact in self.contacts:
            tags.update(contact.get("tags", []))
        return sorted(list(tags))

    def validate_contact(self, name: str, phone1: str, phone2: str, email: str,
                        birthday: str, tags: str) -> tuple[bool, str]:
        """Validate contact fields. Returns (is_valid, error_message)"""
        name = name.strip()
        phone1 = phone1.strip()
        phone2 = phone2.strip()
        email = email.strip()
        birthday = birthday.strip()
        tags = tags.strip()

        if not name:
            return False, "Name is required!"

        if len(name) > 100:
            return False, "Name must be 100 characters or less!"

        if phone1 and not self._is_valid_phone(phone1):
            return False, "Phone 1 format invalid! Use digits, spaces, +, -, ()"

        if phone2 and not self._is_valid_phone(phone2):
            return False, "Phone 2 format invalid! Use digits, spaces, +, -, ()"

        if email and not self._is_valid_email(email):
            return False, "Email format invalid! Example: user@example.com"

        if birthday and not self._is_valid_birthday(birthday):
            return False, "Birthday format invalid! Use YYYY-MM-DD"

        if tags and not self._is_valid_tags(tags):
            return False, "Tags format invalid! Use comma-separated values"

        return True, ""

    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        allowed_chars = set("0123456789+- ()")
        return all(c in allowed_chars for c in phone) and len(phone) >= 7

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        if len(email) < 5 or len(email) > 254:
            return False
        if email.count("@") != 1:
            return False
        local, domain = email.split("@")
        if not local or not domain:
            return False
        if "." not in domain:
            return False
        if domain.startswith(".") or domain.endswith("."):
            return False
        return True

    def _is_valid_birthday(self, birthday: str) -> bool:
        """Validate birthday format YYYY-MM-DD"""
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_valid_tags(self, tags: str) -> bool:
        """Validate tags format (comma-separated)"""
        if not tags:
            return True
        tag_list = [t.strip() for t in tags.split(",")]
        return all(len(t) > 0 and len(t) <= 50 for t in tag_list)
