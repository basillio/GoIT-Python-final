import argparse
import json
import sys
import os
from datetime import datetime
from phonebook import Phonebook
from notes import NotesManager


class PhonebookCLI:
    def __init__(self):
        self.phonebook = Phonebook("contacts.json")
        self.notes_manager = NotesManager("notes.json")
        self.current_contact_id = None
        self.current_note_id = None

    def run(self):
        # Check if running in interactive mode (no arguments)
        if len(sys.argv) == 1:
            self.interactive_menu()
            return

        parser = argparse.ArgumentParser(description="Assistant Phonebook CLI")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Contact commands
        contact_parser = subparsers.add_parser("contact", help="Contact management")
        contact_subparsers = contact_parser.add_subparsers(dest="action")

        contact_subparsers.add_parser("list", help="List all contacts")
        contact_subparsers.add_parser("interactive", help="Interactive contact menu")

        add_parser = contact_subparsers.add_parser("add", help="Add new contact")
        add_parser.add_argument("--name", required=True, help="Contact name")
        add_parser.add_argument("--phone1", help="Phone 1")
        add_parser.add_argument("--phone2", help="Phone 2")
        add_parser.add_argument("--email", help="Email")
        add_parser.add_argument("--birthday", help="Birthday (YYYY-MM-DD)")
        add_parser.add_argument("--tags", help="Tags (comma-separated)")
        add_parser.add_argument("--note", help="Note")

        search_parser = contact_subparsers.add_parser("search", help="Search contacts")
        search_parser.add_argument("query", help="Search query")

        view_parser = contact_subparsers.add_parser("view", help="View contact details")
        view_parser.add_argument("contact_id", help="Contact ID")

        update_parser = contact_subparsers.add_parser("update", help="Update contact")
        update_parser.add_argument("contact_id", help="Contact ID")
        update_parser.add_argument("--name", help="Contact name")
        update_parser.add_argument("--phone1", help="Phone 1")
        update_parser.add_argument("--phone2", help="Phone 2")
        update_parser.add_argument("--email", help="Email")
        update_parser.add_argument("--birthday", help="Birthday (YYYY-MM-DD)")
        update_parser.add_argument("--tags", help="Tags (comma-separated)")
        update_parser.add_argument("--note", help="Note")

        delete_parser = contact_subparsers.add_parser("delete", help="Delete contact")
        delete_parser.add_argument("contact_id", help="Contact ID")

        # Note commands
        note_parser = subparsers.add_parser("note", help="Note management")
        note_subparsers = note_parser.add_subparsers(dest="action")

        note_subparsers.add_parser("list", help="List all notes")
        note_subparsers.add_parser("interactive", help="Interactive note menu")

        note_add_parser = note_subparsers.add_parser("add", help="Add new note")
        note_add_parser.add_argument("--title", required=True, help="Note title")
        note_add_parser.add_argument("--content", required=True, help="Note content")
        note_add_parser.add_argument("--tags", help="Tags (comma-separated)")

        note_search_parser = note_subparsers.add_parser("search", help="Search notes")
        note_search_parser.add_argument("query", help="Search query")

        note_view_parser = note_subparsers.add_parser("view", help="View note details")
        note_view_parser.add_argument("note_id", help="Note ID")

        note_update_parser = note_subparsers.add_parser("update", help="Update note")
        note_update_parser.add_argument("note_id", help="Note ID")
        note_update_parser.add_argument("--title", help="Note title")
        note_update_parser.add_argument("--content", help="Note content")
        note_update_parser.add_argument("--tags", help="Tags (comma-separated)")

        note_delete_parser = note_subparsers.add_parser("delete", help="Delete note")
        note_delete_parser.add_argument("note_id", help="Note ID")

        # Search commands
        search_parser = subparsers.add_parser("search", help="Global search")
        search_parser.add_argument("query", help="Search query")

        # Birthday commands
        birthday_parser = subparsers.add_parser("birthday", help="Birthday management")
        birthday_subparsers = birthday_parser.add_subparsers(dest="action")

        upcoming_parser = birthday_subparsers.add_parser("upcoming", help="Show upcoming birthdays")
        upcoming_parser.add_argument("--days", type=int, default=30, help="Days ahead (0-365)")

        birthday_subparsers.add_parser("today", help="Show today's birthdays")

        # Settings commands
        settings_parser = subparsers.add_parser("settings", help="Settings management")
        settings_subparsers = settings_parser.add_subparsers(dest="action")

        settings_subparsers.add_parser("show", help="Show notification settings")

        set_parser = settings_subparsers.add_parser("set", help="Set notification days")
        set_parser.add_argument("days", nargs="+", type=int, help="Days before birthday (space-separated)")

        args = parser.parse_args()

        if args.command == "contact":
            self.handle_contact(args)
        elif args.command == "note":
            self.handle_note(args)
        elif args.command == "search":
            self.handle_global_search(args)
        elif args.command == "birthday":
            self.handle_birthday(args)
        elif args.command == "settings":
            self.handle_settings(args)
        else:
            parser.print_help()

    def interactive_menu(self):
        """Interactive menu mode"""
        while True:
            print("\n" + "="*60)
            print("Assistant Phonebook - Interactive Menu")
            print("="*60)
            print("\nMain Menu:")
            print("  1. Contacts")
            print("  2. Notes")
            print("  3. Birthday Management")
            print("  4. Global Search")
            print("  5. Settings")
            print("  6. Exit")
            print("\nEnter your choice (1-6): ", end="")

            choice = input().strip()

            if choice == "1":
                self.contact_menu()
            elif choice == "2":
                self.note_menu()
            elif choice == "3":
                self.birthday_menu()
            elif choice == "4":
                self.search_menu()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    def contact_menu(self):
        """Contact management menu"""
        while True:
            print("\n" + "-"*60)
            print("Contact Management")
            print("-"*60)
            print("\n  1. List all contacts")
            print("  2. Add new contact")
            print("  3. Search contacts")
            print("  4. View contact details")
            print("  5. Update contact")
            print("  6. Delete contact")
            print("  7. Back to main menu")
            print("\nEnter your choice (1-7): ", end="")

            choice = input().strip()

            if choice == "1":
                self.list_contacts()
            elif choice == "2":
                self.add_contact_interactive()
            elif choice == "3":
                query = input("Enter search query: ").strip()
                if query:
                    self.search_contacts(query)
            elif choice == "4":
                contact_id = input("Enter contact ID: ").strip()
                if contact_id:
                    self.view_contact(contact_id)
            elif choice == "5":
                contact_id = input("Enter contact ID: ").strip()
                if contact_id:
                    self.update_contact_interactive(contact_id)
            elif choice == "6":
                contact_id = input("Enter contact ID: ").strip()
                if contact_id:
                    confirm = input("Are you sure? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        self.delete_contact(contact_id)
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

    def note_menu(self):
        """Note management menu"""
        while True:
            print("\n" + "-"*60)
            print("Note Management")
            print("-"*60)
            print("\n  1. List all notes")
            print("  2. Add new note")
            print("  3. Search notes")
            print("  4. View note details")
            print("  5. Update note")
            print("  6. Delete note")
            print("  7. Back to main menu")
            print("\nEnter your choice (1-7): ", end="")

            choice = input().strip()

            if choice == "1":
                self.list_notes()
            elif choice == "2":
                self.add_note_interactive()
            elif choice == "3":
                query = input("Enter search query: ").strip()
                if query:
                    self.search_notes(query)
            elif choice == "4":
                note_id = input("Enter note ID: ").strip()
                if note_id:
                    self.view_note(note_id)
            elif choice == "5":
                note_id = input("Enter note ID: ").strip()
                if note_id:
                    self.update_note_interactive(note_id)
            elif choice == "6":
                note_id = input("Enter note ID: ").strip()
                if note_id:
                    confirm = input("Are you sure? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        self.delete_note(note_id)
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

    def birthday_menu(self):
        """Birthday management menu"""
        while True:
            print("\n" + "-"*60)
            print("Birthday Management")
            print("-"*60)
            print("\n  1. Show upcoming birthdays")
            print("  2. Show today's birthdays")
            print("  3. Back to main menu")
            print("\nEnter your choice (1-3): ", end="")

            choice = input().strip()

            if choice == "1":
                days_input = input("Enter days ahead (0-365, default 30): ").strip()
                days = int(days_input) if days_input else 30
                self.show_upcoming_birthdays(days)
            elif choice == "2":
                self.show_today_birthdays()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

    def search_menu(self):
        """Global search menu"""
        query = input("Enter search query: ").strip()
        if query:
            self.handle_global_search(type('args', (), {'query': query})())

    def settings_menu(self):
        """Settings menu"""
        while True:
            print("\n" + "-"*60)
            print("Settings")
            print("-"*60)
            print("\n  1. Show notification settings")
            print("  2. Set notification days")
            print("  3. Back to main menu")
            print("\nEnter your choice (1-3): ", end="")

            choice = input().strip()

            if choice == "1":
                self.show_settings()
            elif choice == "2":
                days_input = input("Enter notification days (space-separated, e.g., 0 1 3 7): ").strip()
                if days_input:
                    try:
                        days = [int(d) for d in days_input.split()]
                        self.set_notification_days(days)
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by spaces.")
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

    def add_contact_interactive(self):
        """Add contact interactively with validation"""
        print("\n" + "-"*60)
        print("Add New Contact")
        print("-"*60)

        while True:
            name = input("Name (required): ").strip()
            if not name:
                print("ERROR: Name is required!")
                continue
            if len(name) > 100:
                print("ERROR: Name must be 100 characters or less!")
                continue
            break

        phone1 = input("Enter phone 1 (e.g., +1555012355): ").strip()
        while phone1 and not self.phonebook._is_valid_phone(phone1):
            print("ERROR: Phone 1 format invalid! Use digits, spaces, +, -, ()")
            print("Example: +1-555-0123, (555) 123-4567, +1555012355")
            phone1 = input("Phone 1: ").strip()

        phone2 = input("Enter phone 2 (or press Enter to skip): ").strip()
        while phone2 and not self.phonebook._is_valid_phone(phone2):
            print("ERROR: Phone 2 format invalid! Use digits, spaces, +, -, ()")
            print("Example: +1-555-0123 or (555) 123-4567")
            phone2 = input("Phone 2: ").strip()

        email = input("Email (e.g., user@domain.com, or Enter to skip): ").strip()
        while email and not self.phonebook._is_valid_email(email):
            print("ERROR: Email format invalid!")
            print("Example: john@example.com")
            email = input("Email: ").strip()

        birthday = input("Birthday (YYYY-MM-DD) (e.g., 1995-05-30, or Enter):").strip()
        while birthday and not self.phonebook._is_valid_birthday(birthday):
            print("ERROR: Birthday format invalid!")
            print("Example: 1990-05-15")
            birthday = input("Birthday (YYYY-MM-DD): ").strip()

        tags_input = input("Enter tags separated by commas (e.g., work, vip, friend): ").strip()
        while tags_input and not self.phonebook._is_valid_tags(tags_input):
            print("ERROR: Tags format invalid!")
            print("Example: work, friend, important")
            tags_input = input("Tags (comma-separated): ").strip()

        note = input("Note (any additional notes/details or Enter to skip): ").strip()

        class Args:
            pass

        args = Args()
        args.name = name
        args.phone1 = phone1
        args.phone2 = phone2
        args.email = email
        args.birthday = birthday
        args.tags = tags_input
        args.note = note

        self.add_contact(args)

    def update_contact_interactive(self, contact_id):
        """Update contact interactively with validation"""
        contact = self.phonebook.get_contact(contact_id)
        if not contact:
            print(f"Contact not found (ID: {contact_id})")
            return

        print("\n" + "-"*60)
        print("Update Contact")
        print("-"*60)
        print(f"Current values (press Enter to keep):")
        print(f"  Name: {contact['name']}")
        print(f"  Phone 1: {contact['phone1']}")
        print(f"  Phone 2: {contact['phone2']}")
        print(f"  Email: {contact['email']}")
        print(f"  Birthday: {contact['birthday']}")
        print(f"  Tags: {', '.join(contact['tags'])}")
        print()

        # Name validation
        name = input("Name: ").strip()
        if name and len(name) > 100:
            while len(name) > 100:
                print("ERROR: Name must be 100 characters or less!")
                name = input("Name: ").strip()
        name = name or None

        # Phone 1 validation
        phone1 = input("Phone 1: ").strip()
        while phone1 and not self.phonebook._is_valid_phone(phone1):
            print("ERROR: Phone 1 format invalid! Use digits, spaces, +, -, ()")
            print("Example: +1-555-0123 or (555) 123-4567")
            phone1 = input("Phone 1: ").strip()
        phone1 = phone1 or None

        # Phone 2 validation
        phone2 = input("Phone 2: ").strip()
        while phone2 and not self.phonebook._is_valid_phone(phone2):
            print("ERROR: Phone 2 format invalid! Use digits, spaces, +, -, ()")
            print("Example: +1-555-0123 or (555) 123-4567")
            phone2 = input("Phone 2: ").strip()
        phone2 = phone2 or None

        # Email validation
        email = input("Email: ").strip()
        while email and not self.phonebook._is_valid_email(email):
            print("ERROR: Email format invalid!")
            print("Example: john@example.com")
            email = input("Email: ").strip()
        email = email or None

        # Birthday validation
        birthday = input("Birthday (YYYY-MM-DD): ").strip()
        while birthday and not self.phonebook._is_valid_birthday(birthday):
            print("ERROR: Birthday format invalid!")
            print("Example: 1990-05-15")
            birthday = input("Birthday (YYYY-MM-DD): ").strip()
        birthday = birthday or None

        # Tags validation
        tags_input = input("Tags (comma-separated): ").strip()
        while tags_input and not self.phonebook._is_valid_tags(tags_input):
            print("ERROR: Tags format invalid!")
            print("Example: work, friend, important")
            tags_input = input("Tags (comma-separated): ").strip()
        tags_input = tags_input or None

        class Args:
            pass

        args = Args()
        args.contact_id = contact_id
        args.name = name
        args.phone1 = phone1
        args.phone2 = phone2
        args.email = email
        args.birthday = birthday
        args.tags = tags_input
        args.note = None

        self.update_contact(args)

    def add_note_interactive(self):
        """Add note interactively"""
        print("\n" + "-"*60)
        print("Add New Note")
        print("-"*60)
        title = input("Title (required): ").strip()
        if not title:
            print("Title is required!")
            return

        print("Content (enter multiple lines, type 'END' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        content = "\n".join(lines)

        if not content.strip():
            print("Content is required!")
            return

        tags_input = input("Tags (comma-separated): ").strip()
        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []

        class Args:
            pass

        args = Args()
        args.title = title
        args.content = content
        args.tags = tags_input

        self.add_note(args)

    def update_note_interactive(self, note_id):
        """Update note interactively"""
        note = self.notes_manager.get_note(note_id)
        if not note:
            print(f"Note not found (ID: {note_id})")
            return

        print("\n" + "-"*60)
        print("Update Note")
        print("-"*60)
        print(f"Current title: {note['title']}")
        print(f"Current tags: {', '.join(note['tags'])}")
        print()

        title = input("Title (press Enter to keep): ").strip() or None
        print("Content (press Enter to keep, or enter new content):")
        print("(enter multiple lines, type 'END' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        content = "\n".join(lines) if lines else None

        tags_input = input("Tags (comma-separated, press Enter to keep): ").strip() or None

        class Args:
            pass

        args = Args()
        args.note_id = note_id
        args.title = title
        args.content = content
        args.tags = tags_input

        self.update_note(args)



    def handle_contact(self, args):
        if args.action == "list":
            self.list_contacts()
        elif args.action == "add":
            self.add_contact(args)
        elif args.action == "search":
            self.search_contacts(args.query)
        elif args.action == "view":
            self.view_contact(args.contact_id)
        elif args.action == "update":
            self.update_contact(args)
        elif args.action == "delete":
            self.delete_contact(args.contact_id)
        else:
            print("Contact action required: list, add, search, view, update, delete")

    def handle_note(self, args):
        if args.action == "list":
            self.list_notes()
        elif args.action == "add":
            self.add_note(args)
        elif args.action == "search":
            self.search_notes(args.query)
        elif args.action == "view":
            self.view_note(args.note_id)
        elif args.action == "update":
            self.update_note(args)
        elif args.action == "delete":
            self.delete_note(args.note_id)
        else:
            print("Note action required: list, add, search, view, update, delete")

    def handle_global_search(self, args):
        contacts = self.phonebook.search_contacts(args.query)
        notes = self.notes_manager.search_notes(args.query)

        print(f"\nGlobal Search Results for '{args.query}':")
        print("=" * 60)

        if contacts:
            print(f"\nContacts ({len(contacts)}):")
            for contact in contacts:
                print(f"  - {contact['name']} ({contact['id']})")
                if contact.get('phone1'):
                    print(f"    Phone: {contact['phone1']}")
                if contact.get('email'):
                    print(f"    Email: {contact['email']}")

        if notes:
            print(f"\nNotes ({len(notes)}):")
            for note in notes:
                print(f"  - {note['title']} ({note['id']})")

        if not contacts and not notes:
            print("No results found")

    def handle_birthday(self, args):
        if args.action == "upcoming":
            self.show_upcoming_birthdays(args.days)
        elif args.action == "today":
            self.show_today_birthdays()
        else:
            print("Birthday action required: upcoming, today")

    def handle_settings(self, args):
        if args.action == "show":
            self.show_settings()
        elif args.action == "set":
            self.set_notification_days(args.days)
        else:
            print("Settings action required: show, set")

    def list_contacts(self):
        if not self.phonebook.contacts:
            print("No contacts found")
            return

        print(f"\nContacts ({len(self.phonebook.contacts)}):")
        print("=" * 80)
        for contact in self.phonebook.contacts:
            print(f"ID: {contact['id']}")
            print(f"Name: {contact['name']}")
            if contact.get('phone1'):
                print(f"Phone 1: {contact['phone1']}")
            if contact.get('phone2'):
                print(f"Phone 2: {contact['phone2']}")
            if contact.get('email'):
                print(f"Email: {contact['email']}")
            if contact.get('birthday'):
                print(f"Birthday: {contact['birthday']}")
            if contact.get('tags'):
                print(f"Tags: {', '.join(contact['tags'])}")
            print("-" * 80)

    def add_contact(self, args):
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

        result = self.phonebook.add_contact(
            name=args.name,
            phone1=args.phone1 or "",
            phone2=args.phone2 or "",
            email=args.email or "",
            birthday=args.birthday or "",
            note=args.note or "",
            tags=tags
        )
        if result:
            print(f"Contact added successfully")
        else:
            print("Failed to add contact")

    def search_contacts(self, query):
        results = self.phonebook.search_contacts(query)
        if not results:
            print(f"No contacts found for '{query}'")
            return

        print(f"\nSearch Results for '{query}' ({len(results)} found):")
        print("=" * 80)
        for contact in results:
            print(f"ID: {contact['id']}")
            print(f"Name: {contact['name']}")
            if contact.get('phone1'):
                print(f"Phone 1: {contact['phone1']}")
            if contact.get('email'):
                print(f"Email: {contact['email']}")
            print("-" * 80)

    def view_contact(self, contact_id):
        contact = self.phonebook.get_contact(contact_id)
        if not contact:
            print(f"Contact not found (ID: {contact_id})")
            return

        print(f"\nContact Details:")
        print("=" * 60)
        print(f"ID: {contact['id']}")
        print(f"Name: {contact['name']}")
        print(f"Phone 1: {contact.get('phone1', 'N/A')}")
        print(f"Phone 2: {contact.get('phone2', 'N/A')}")
        print(f"Email: {contact.get('email', 'N/A')}")
        print(f"Birthday: {contact.get('birthday', 'N/A')}")
        print(f"Tags: {', '.join(contact.get('tags', [])) or 'N/A'}")
        print(f"Note: {contact.get('note', 'N/A')}")

    def update_contact(self, args):
        contact = self.phonebook.get_contact(args.contact_id)
        if not contact:
            print(f"Contact not found (ID: {args.contact_id})")
            return

        name = args.name or contact['name']
        phone1 = args.phone1 or contact['phone1']
        phone2 = args.phone2 or contact['phone2']
        email = args.email or contact['email']
        birthday = args.birthday or contact['birthday']
        note = args.note or contact['note']
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else contact['tags']

        if self.phonebook.update_contact(args.contact_id, name, phone1, phone2, email, birthday, note, tags):
            print("Contact updated successfully")
        else:
            print("Failed to update contact")

    def delete_contact(self, contact_id):
        if self.phonebook.delete_contact(contact_id):
            print("Contact deleted successfully")
        else:
            print(f"Contact not found (ID: {contact_id})")

    def list_notes(self):
        if not self.notes_manager.notes:
            print("No notes found")
            return

        print(f"\nNotes ({len(self.notes_manager.notes)}):")
        print("=" * 80)
        for note in self.notes_manager.notes:
            print(f"ID: {note['id']}")
            print(f"Title: {note['title']}")
            print(f"Content: {note['note'][:100]}..." if len(note['note']) > 100 else f"Content: {note['note']}")
            if note.get('tags'):
                print(f"Tags: {', '.join(note['tags'])}")
            print("-" * 80)

    def add_note(self, args):
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

        result = self.notes_manager.add_note(
            title=args.title,
            note_text=args.content,
            tags=tags
        )
        if result:
            print(f"Note added successfully")
        else:
            print("Failed to add note")

    def search_notes(self, query):
        sort_choice = input("Sort results by tags count? (y/n, default: n): ").strip().lower()
        sort_by_tags = True if sort_choice == 'y' else False
        results = self.notes_manager.search_notes(query, sort_by_tags_count=sort_by_tags)
        if not results:
            print(f"No notes found for '{query}'")
            return

        print(f"\nSearch Results for '{query}' ({len(results)} found):")
        print("=" * 80)
        for note in results:
            print(f"ID: {note['id']}")
            print(f"Title: {note['title']}")
            print(f"Content: {note['note'][:100]}..." if len(note['note']) > 100 else f"Content: {note['note']}")
            print(f"Tags: {', '.join(note.get('tags', [])) or 'N/A'}")
            print("-" * 80)

    def view_note(self, note_id):
        note = self.notes_manager.get_note(note_id)
        if not note:
            print(f"Note not found (ID: {note_id})")
            return

        print(f"\nNote Details:")
        print("=" * 60)
        print(f"ID: {note['id']}")
        print(f"Title: {note['title']}")
        print(f"Content:\n{note['note']}")
        print(f"Tags: {', '.join(note.get('tags', [])) or 'N/A'}")

    def update_note(self, args):
        note = self.notes_manager.get_note(args.note_id)
        if not note:
            print(f"Note not found (ID: {args.note_id})")
            return

        title = args.title or note['title']
        content = args.content or note['note']
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else note['tags']

        if self.notes_manager.update_note(args.note_id, title, content, tags):
            print("Note updated successfully")
        else:
            print("Failed to update note")

    def delete_note(self, note_id):
        if self.notes_manager.delete_note(note_id):
            print("Note deleted successfully")
        else:
            print(f"Note not found (ID: {note_id})")

    def show_upcoming_birthdays(self, days):
        if days < 0 or days > 365:
            print("Days must be between 0-365")
            return

        today = datetime.now().date()
        upcoming = []

        for contact in self.phonebook.contacts:
            birthday_str = contact.get("birthday", "")
            if not birthday_str:
                continue

            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                next_birthday = birthday.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                days_until = (next_birthday - today).days

                if 0 <= days_until <= days:
                    upcoming.append((contact.get("name", "Unknown"), days_until, birthday_str))
            except:
                continue

        if not upcoming:
            print(f"No birthdays in next {days} days")
            return

        upcoming.sort(key=lambda x: x[1])
        print(f"\nUpcoming Birthdays (next {days} days):")
        print("=" * 60)
        for name, days_until, birthday in upcoming:
            if days_until == 0:
                print(f"{name}: TODAY (Birthday: {birthday})")
            else:
                print(f"{name}: {days_until} day(s) (Birthday: {birthday})")

    def show_today_birthdays(self):
        today = datetime.now().date()
        today_birthdays = []

        for contact in self.phonebook.contacts:
            birthday_str = contact.get("birthday", "")
            if not birthday_str:
                continue

            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                next_birthday = birthday.replace(year=today.year)
                if next_birthday == today:
                    today_birthdays.append(contact.get("name", "Unknown"))
            except:
                continue

        if not today_birthdays:
            print("No birthdays today")
            return

        print(f"\nToday's Birthdays:")
        print("=" * 60)
        for name in today_birthdays:
            print(f"- {name}")

    def show_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    days = settings.get("notification_days", [0, 1, 3, 7])
                    print(f"Notification days: {days}")
            else:
                print("Notification days: [0, 1, 3, 7] (default)")
        except Exception as e:
            print(f"Error reading settings: {e}")

    def set_notification_days(self, days):
        settings = {"notification_days": days}
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"Notification days set to: {days}")
        except Exception as e:
            print(f"Error saving settings: {e}")


if __name__ == "__main__":
    try:
     cli = PhonebookCLI()
     cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application closed via shortcut. Goodbye!")
