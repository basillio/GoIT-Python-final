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
