import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class NotesManager:
    def __init__(self, filename: str = "notes.json"):
        self.filename = filename
        self.notes: List[Dict] = []
        self.load_notes()

    def load_notes(self):
        """Load notes from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.notes = []
        else:
            self.notes = []

    def save_notes(self):
        """Save notes to JSON file immediately"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving notes: {e}")
            return False

    def add_note(self, title: str, note_text: str, tags: List[str]) -> bool:
        """Add a new note"""
        if not note_text.strip():
            return False

        note = {
            "id": str(uuid.uuid4()),
            "title": title.strip() if title.strip() else self._generate_default_title(),
            "note": note_text.strip(),
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.notes.append(note)
        return self.save_notes()

    def update_note(self, note_id: str, title: str, note_text: str, tags: List[str]) -> bool:
        """Update an existing note"""
        for note in self.notes:
            if note["id"] == note_id:
                note.update({
                    "title": title.strip() if title.strip() else self._generate_default_title(),
                    "note": note_text.strip(),
                    "tags": [tag.strip() for tag in tags if tag.strip()],
                    "modified": datetime.now().isoformat()
                })
                return self.save_notes()
        return False

    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        self.notes = [n for n in self.notes if n["id"] != note_id]
        return self.save_notes()

    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by text or tags"""
        query = query.lower().strip()
        if not query:
            return self.notes

        results = []
        for note in self.notes:
            if (query in note["note"].lower() or
                any(query in tag.lower() for tag in note["tags"])):
                results.append(note)
        return results

    def get_note(self, note_id: str) -> Optional[Dict]:
        """Get a specific note by ID"""
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None

    def get_all_tags(self) -> List[str]:
        """Get all unique tags from all notes"""
        tags = set()
        for note in self.notes:
            tags.update(note.get("tags", []))
        return sorted(list(tags))

    def validate_note(self, title: str, note_text: str, tags: str) -> tuple[bool, str]:
        """Validate note fields. Returns (is_valid, error_message)"""
        title = title.strip()
        note_text = note_text.strip()
        tags = tags.strip()

        if not note_text:
            return False, "Note text is required!"

        if len(note_text) > 5000:
            return False, "Note must be 5000 characters or less!"

        if title and len(title) > 100:
            return False, "Title must be 100 characters or less!"

        if tags and not self._is_valid_tags(tags):
            return False, "Tags format invalid! Use comma-separated values"

        return True, ""

    def _generate_default_title(self) -> str:
        """Generate default title with current date and time"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")

    def _is_valid_tags(self, tags: str) -> bool:
        """Validate tags format (comma-separated)"""
        if not tags:
            return True
        tag_list = [t.strip() for t in tags.split(",")]
        return all(len(t) > 0 and len(t) <= 50 for t in tag_list)
