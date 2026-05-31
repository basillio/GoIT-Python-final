import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from ui_components import (
    SearchComponent, BirthdayComponent, ContactFormComponent,
    ContactCardComponent, NoteFormComponent, TagFilterComponent
)


class PhonebookUI:
    def __init__(self, root, phonebook, notes_manager):
        self.root = root
        self.phonebook = phonebook
        self.notes_manager = notes_manager
        self.current_contact_id = None
        self.contact_ids = []
        self.current_note_id = None
        self.note_ids = []
        self.notification_days = [0, 1, 3, 7]
        self.load_settings()
        self.setup_ui()
        self.refresh_contacts_list()
        self.refresh_notes_list()
        self.check_birthdays()

    def load_settings(self):
        """Load notification settings from config file"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.notification_days = settings.get("notification_days", [0, 1, 3, 7])
            else:
                self.notification_days = [0, 1, 3, 7]
        except Exception as e:
            self.notification_days = [0, 1, 3, 7]

    def setup_ui(self):
        """Setup the main UI layout with tabs"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Create components
        self.search_component = SearchComponent(
            main_frame,
            on_search_change=self.on_global_search_change,
            on_clear=self.clear_global_search
        )

        self.birthday_component = BirthdayComponent(
            main_frame,
            on_show_birthdays=self.show_upcoming_birthdays
        )

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Contacts Tab
        self.contacts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.contacts_tab, text="Contacts")
        self.setup_contacts_tab()

        # Notes Tab
        self.notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.notes_tab, text="Notes")
        self.setup_notes_tab()

    def setup_contacts_tab(self):
        """Setup the Contacts tab"""
        button_frame = ttk.Frame(self.contacts_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

        ttk.Button(button_frame, text="New Contact", command=self.new_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Settings", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(button_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.RIGHT, padx=5)

        content_frame = ttk.Frame(self.contacts_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Left side - contacts list
        left_frame = ttk.LabelFrame(content_frame, text="Contacts List", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.contacts_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=20, font=("Arial", 9))
        self.contacts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.on_contact_select)
        scrollbar.config(command=self.contacts_listbox.yview)

        # Right side - contact details and preview
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create components
        self.card_component = ContactCardComponent(right_frame)
        self.contact_form_component = ContactFormComponent(right_frame)

        # Buttons frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

    def setup_notes_tab(self):
        """Setup the Notes tab"""
        button_frame = ttk.Frame(self.notes_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

        ttk.Button(button_frame, text="New Note", command=self.new_note).pack(side=tk.LEFT, padx=5)

        self.notes_status_var = tk.StringVar(value="Ready")
        ttk.Label(button_frame, textvariable=self.notes_status_var, foreground="blue").pack(side=tk.RIGHT, padx=5)

        content_frame = ttk.Frame(self.notes_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Left side - notes list with filter
        left_frame = ttk.LabelFrame(content_frame, text="Notes List", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Tag filter component
        self.tag_filter_component = TagFilterComponent(
            left_frame,
            on_apply=self.apply_tag_filter,
            on_clear=self.clear_tag_filter
        )

        # Notes treeview with columns
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_treeview = ttk.Treeview(tree_frame, columns=("Title", "Tags"),
                                           show="headings", height=25, yscrollcommand=scrollbar.set)
        self.notes_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.notes_treeview.yview)

        self.notes_treeview.column("Title", width=150, anchor=tk.W)
        self.notes_treeview.column("Tags", width=100, anchor=tk.W)
        self.notes_treeview.heading("Title", text="Title", command=lambda: self.sort_notes_by_column("Title"))
        self.notes_treeview.heading("Tags", text="Tags", command=lambda: self.sort_notes_by_column("Tags"))

        self.notes_treeview.bind('<<TreeviewSelect>>', self.on_note_select)
        self.notes_tree_ids = {}

        # Right side - note details
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.note_form_component = NoteFormComponent(right_frame)

        # Buttons frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_note_form).pack(side=tk.LEFT, padx=5)

    def refresh_contacts_list(self, contacts=None):
        """Refresh the contacts listbox"""
        self.contacts_listbox.delete(0, tk.END)
        self.contact_ids = []
        if contacts is None:
            contacts = self.phonebook.contacts

        for contact in contacts:
            display_text = f"{contact['name']} - {contact['phone1']}"
            self.contacts_listbox.insert(tk.END, display_text)
            self.contact_ids.append(contact["id"])

    def on_contact_select(self, event):
        """Handle contact selection from listbox"""
        selection = self.contacts_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self.contact_ids):
            self.current_contact_id = self.contact_ids[index]
            contact = self.phonebook.get_contact(self.current_contact_id)
            if contact:
                self.contact_form_component.set_data(contact)
                self.card_component.update(contact)

    def new_contact(self):
        """Prepare form for new contact"""
        self.current_contact_id = None
        self.clear_form()
        self.contacts_listbox.selection_clear(0, tk.END)

    def clear_form(self):
        """Clear all form fields"""
        self.contact_form_component.clear()
        self.current_contact_id = None

    def save_contact(self):
        """Save or update contact"""
        data = self.contact_form_component.get_data()
        tags = [tag.strip() for tag in data['tags'].split(",") if tag.strip()]

        is_valid, error_msg = self.phonebook.validate_contact(
            data['name'], data['phone1'], data['phone2'],
            data['email'], data['birthday'], data['tags']
        )
        if not is_valid:
            formatted_error = self._format_error_message(error_msg)
            messagebox.showwarning("Validation Error", formatted_error)
            return

        if self.current_contact_id:
            if self.phonebook.update_contact(
                self.current_contact_id, data['name'], data['phone1'],
                data['phone2'], data['email'], data['birthday'], data['note'], tags
            ):
                self.status_var.set("Contact updated and saved to contacts.json")
                messagebox.showinfo("Success", "Contact updated successfully!")
                self.refresh_contacts_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update contact!")
        else:
            if self.phonebook.add_contact(
                data['name'], data['phone1'], data['phone2'],
                data['email'], data['birthday'], data['note'], tags
            ):
                self.status_var.set("New contact added and saved to contacts.json")
                messagebox.showinfo("Success", "Contact added successfully!")
                self.refresh_contacts_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to add contact!")

    def _format_error_message(self, error_msg: str) -> str:
        """Format error message with helpful examples"""
        error_templates = {
            "Name is required!": "Name is required!\n\nExample: John Doe",
            "Name must be 100 characters or less!": "Name must be 100 characters or less!\n\nExample: John Doe",
            "Phone 1 format invalid!": "Phone 1 format invalid!\n\nValid formats:\n• 555-1234\n• +1 (555) 123-4567\n• 555 123 4567\n• +44-20-7946-0958",
            "Phone 2 format invalid!": "Phone 2 format invalid!\n\nValid formats:\n• 555-1234\n• +1 (555) 123-4567\n• 555 123 4567\n• +44-20-7946-0958",
            "Email format invalid!": "Email format invalid!\n\nValid formats:\n• john@example.com\n• jane.doe@company.co.uk\n• contact+tag@domain.org",
            "Birthday format invalid!": "Birthday format invalid!\n\nUse YYYY-MM-DD format\n\nExamples:\n• 1990-05-15\n• 2000-12-25\n• 1985-01-01",
            "Tags format invalid!": "Tags format invalid!\n\nUse comma-separated values\n\nExamples:\n• friend\n• friend, work\n• family, close friend, colleague",
        }

        for key, template in error_templates.items():
            if key in error_msg:
                return template

        return error_msg

    def delete_contact(self):
        """Delete the current contact"""
        if not self.current_contact_id:
            messagebox.showwarning("Warning", "No contact selected!")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this contact?"):
            if self.phonebook.delete_contact(self.current_contact_id):
                self.status_var.set("Contact deleted and removed from contacts.json")
                messagebox.showinfo("Success", "Contact deleted successfully!")
                self.refresh_contacts_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to delete contact!")

    def open_settings(self):
        """Open settings window for birthday notifications"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings - Birthday Notifications")
        settings_window.geometry("400x650")
        settings_window.resizable(False, False)

        main_frame = ttk.Frame(settings_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Birthday Notification Settings", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 15))

        ttk.Label(main_frame, text="Configure when to receive birthday notifications:", font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 10))

        options_frame = ttk.LabelFrame(main_frame, text="Notification Days Before Birthday", padding=10)
        options_frame.pack(fill=tk.X, pady=10)

        self.notify_vars = {}
        notification_options = [
            ("On the day of birthday", 0),
            ("1 day before birthday", 1),
            ("2 days before birthday", 2),
            ("3 days before birthday", 3),
            ("7 days before birthday", 7),
            ("14 days before birthday", 14),
        ]

        for label, days in notification_options:
            var = tk.BooleanVar(value=(days in self.notification_days))
            self.notify_vars[days] = var
            ttk.Checkbutton(options_frame, text=label, variable=var).pack(anchor=tk.W, pady=3)

        info_frame = ttk.LabelFrame(main_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        info_text = """Select which days before a birthday you want to be notified:

• On the day: Get notified on the actual birthday
• 1 day before: Reminder one day in advance
• 2 days before: Early reminder for planning
• 3 days before: Early reminder for planning
• 7 days before: Week-long advance notice
• 14 days before: Two weeks notice

Notifications will appear when you open the application."""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 8)).pack(anchor=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save", command=lambda: self.save_settings(settings_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)

    def save_settings(self, window):
        """Save notification settings to config file"""
        enabled_days = [days for days, var in self.notify_vars.items() if var.get()]
        self.notification_days = sorted(enabled_days)

        settings = {"notification_days": self.notification_days}

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Settings Saved", f"Birthday notifications enabled for:\n{', '.join([str(d) + ' days before' if d > 0 else 'On birthday' for d in self.notification_days])}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def check_birthdays(self):
        """Check for upcoming birthdays and display notifications"""
        today = datetime.now().date()
        upcoming_birthdays = []

        for contact in self.phonebook.contacts:
            birthday_str = contact.get('birthday', '')
            if not birthday_str:
                continue

            try:
                birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
                this_year_birthday = birthday.replace(year=today.year)

                if this_year_birthday < today:
                    this_year_birthday = birthday.replace(year=today.year + 1)

                days_until = (this_year_birthday - today).days

                if days_until in self.notification_days:
                    name = contact.get('name', 'Unknown')
                    if days_until == 0:
                        upcoming_birthdays.append(f"Birthday: {name} - TODAY!")
                    else:
                        upcoming_birthdays.append(f"Birthday: {name} - in {days_until} day(s)")
            except ValueError:
                continue

        if upcoming_birthdays:
            notification_text = "Upcoming Birthdays:\n\n" + "\n".join(upcoming_birthdays)
            self.root.after(100, lambda: messagebox.showinfo("Birthday Notifications", notification_text))

    def refresh_notes_list(self, notes=None, update_tag_filter=True):
        """Refresh the notes treeview"""
        for item in self.notes_treeview.get_children():
            self.notes_treeview.delete(item)
        self.notes_tree_ids = {}

        if notes is None:
            notes = self.notes_manager.notes

        # Extract all unique tags from all notes (not just displayed ones)
        if update_tag_filter:
            all_tags = set()
            for note in self.notes_manager.notes:
                all_tags.update(note.get('tags', []))
            all_tags = sorted(list(all_tags))

            # Get currently selected tags from the filter
            selected_tags = self.tag_filter_component.get_selected()

            # Update tag filter with available tags and maintain selection
            self.tag_filter_component.update_list(all_tags=all_tags, selected_tags=selected_tags)

        for note in notes:
            title = note.get('title', 'Untitled')
            tags_str = ", ".join(note.get('tags', []))
            item_id = self.notes_treeview.insert("", "end", values=(title, tags_str))
            self.notes_tree_ids[item_id] = note["id"]

    def on_note_select(self, event):
        """Handle note selection from treeview"""
        selection = self.notes_treeview.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id in self.notes_tree_ids:
            self.current_note_id = self.notes_tree_ids[item_id]
            note = self.notes_manager.get_note(self.current_note_id)
            if note:
                self.note_form_component.set_data(note)

    def new_note(self):
        """Prepare form for new note"""
        self.current_note_id = None
        self.clear_note_form()
        self.notes_treeview.selection_remove(self.notes_treeview.selection())

    def clear_note_form(self):
        """Clear all note form fields"""
        self.note_form_component.clear()
        self.current_note_id = None

    def save_note(self):
        """Save or update note"""
        data = self.note_form_component.get_data()
        tags = [tag.strip() for tag in data['tags'].split(",") if tag.strip()]

        is_valid, error_msg = self.notes_manager.validate_note(data['title'], data['content'], data['tags'])
        if not is_valid:
            formatted_error = self._format_note_error_message(error_msg)
            messagebox.showwarning("Validation Error", formatted_error)
            return

        if self.current_note_id:
            if self.notes_manager.update_note(self.current_note_id, data['title'], data['content'], tags):
                self.notes_status_var.set("Note updated and saved to notes.json")
                messagebox.showinfo("Success", "Note updated successfully!")
                self.refresh_notes_list()
                self.clear_note_form()
            else:
                messagebox.showerror("Error", "Failed to update note!")
        else:
            if self.notes_manager.add_note(data['title'], data['content'], tags):
                self.notes_status_var.set("New note added and saved to notes.json")
                messagebox.showinfo("Success", "Note added successfully!")
                self.refresh_notes_list()
                self.clear_note_form()
            else:
                messagebox.showerror("Error", "Failed to add note!")

    def delete_note(self):
        """Delete the current note"""
        if not self.current_note_id:
            messagebox.showwarning("Warning", "No note selected!")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            if self.notes_manager.delete_note(self.current_note_id):
                self.notes_status_var.set("Note deleted and removed from notes.json")
                messagebox.showinfo("Success", "Note deleted successfully!")
                self.refresh_notes_list()
                self.clear_note_form()
            else:
                messagebox.showerror("Error", "Failed to delete note!")

    def _format_note_error_message(self, error_msg: str) -> str:
        """Format note error message with helpful examples"""
        error_templates = {
            "Note text is required!": "Note text is required!\n\nExample: Meeting notes from today's standup",
            "Note must be 5000 characters or less!": "Note must be 5000 characters or less!\n\nExample: Meeting notes from today's standup",
            "Title must be 100 characters or less!": "Title must be 100 characters or less!\n\nExample: 2026-05-28 14:30",
            "Tags format invalid!": "Tags format invalid!\n\nUse comma-separated values\n\nExamples:\n• important\n• important, work\n• meeting, follow-up, urgent",
        }

        for key, template in error_templates.items():
            if key in error_msg:
                return template

        return error_msg

    def on_global_search_change(self):
        """Handle global search input changes across all tabs"""
        search_term = self.search_component.get_value()

        if not search_term:
            self.search_component.set_results_text("Ready")
            self.search_component.close_dropdown()
            return

        contacts_results = self.phonebook.search_contacts(search_term)
        notes_results = self.notes_manager.search_notes(search_term)

        contact_count = len(contacts_results)
        notes_count = len(notes_results)

        if contact_count == 0 and notes_count == 0:
            self.search_component.set_results_text("No results found")
            self.search_component.close_dropdown()
            return

        result_text = []
        if contact_count > 0:
            result_text.append(f"{contact_count} Contact{'s' if contact_count != 1 else ''}")
        if notes_count > 0:
            result_text.append(f"{notes_count} Note{'s' if notes_count != 1 else ''}")

        self.search_component.set_results_text(" | ".join(result_text) + " found")

        results_data = []
        for contact in contacts_results:
            display_text = f"[Contact] {contact.get('name', 'Unknown')}"
            if contact.get('phone1'):
                display_text += f" - {contact['phone1']}"
            results_data.append(('contact', contact, display_text))

        for note in notes_results:
            display_text = f"[Note] {note.get('title', 'Untitled')}"
            results_data.append(('note', note, display_text))

        self.search_component.show_dropdown(results_data)
        self.search_component.results_listbox.bind('<<ListboxSelect>>', self.on_search_result_select)

    def on_search_result_select(self, event):
        """Handle search result selection from dropdown"""
        selection = self.search_component.results_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        result_type, result_data, _ = self.search_component.results_data[index]

        if result_type == 'contact':
            self.notebook.select(0)
            self.current_contact_id = result_data.get('id')
            self.contact_form_component.set_data(result_data)
            self.card_component.update(result_data)

            self.refresh_contacts_list()
            for i, contact_id in enumerate(self.contact_ids):
                if contact_id == self.current_contact_id:
                    self.contacts_listbox.selection_clear(0, tk.END)
                    self.contacts_listbox.selection_set(i)
                    self.contacts_listbox.see(i)
                    break

        elif result_type == 'note':
            self.notebook.select(1)
            self.current_note_id = result_data.get('id')
            self.note_form_component.set_data(result_data)

            self.refresh_notes_list()
            for tree_item_id, note_id in self.notes_tree_ids.items():
                if note_id == self.current_note_id:
                    self.notes_treeview.selection_set(tree_item_id)
                    self.notes_treeview.see(tree_item_id)
                    break

        self.search_component.close_dropdown()

    def clear_global_search(self):
        """Clear global search and reset results"""
        self.search_component.clear()

    def show_upcoming_birthdays(self):
        """Show contacts with birthdays within specified days"""
        try:
            days = self.birthday_component.get_days()
            if days is None:
                self.birthday_component.set_results("Please enter number of days")
                return

            if days < 0 or days > 365:
                self.birthday_component.set_results("Days must be between 0-365")
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

            if upcoming:
                upcoming.sort(key=lambda x: x[1])
                result_text = f"{len(upcoming)} birthday(s): "
                details = []
                for name, days_until, birthday in upcoming:
                    if days_until == 0:
                        details.append(f"{name} (TODAY)")
                    else:
                        details.append(f"{name} ({days_until}d)")
                result_text += " | ".join(details)
                self.birthday_component.set_results(result_text)
            else:
                self.birthday_component.set_results(f"No birthdays in next {days} days")

        except ValueError:
            self.birthday_component.set_results("Invalid input - enter number 0-365")
        except Exception as e:
            self.birthday_component.set_results("Error: " + str(e))

    def sort_notes_by_column(self, column):
        """Sort notes by column (Title or Tags)"""
        all_notes = self.notes_manager.notes

        if column == "Title":
            sorted_notes = sorted(all_notes, key=lambda x: x.get('title', 'Untitled').lower())
        elif column == "Tags":
            sorted_notes = sorted(all_notes, key=lambda x: ", ".join(x.get('tags', [])).lower())
        else:
            sorted_notes = all_notes

        self.refresh_notes_list(sorted_notes)

    def apply_tag_filter(self, selected_tags):
        """Apply tag filter to notes"""
        if not selected_tags:
            self.tag_filter_component.set_selected_display([])
            self.refresh_notes_list(update_tag_filter=True)
        else:
            self.tag_filter_component.set_selected_display(selected_tags)
            filtered_notes = [note for note in self.notes_manager.notes
                            if any(tag in note.get('tags', []) for tag in selected_tags)]
            self.refresh_notes_list(filtered_notes, update_tag_filter=False)

    def clear_tag_filter(self):
        """Clear tag filter"""
        self.tag_filter_component.set_selected_display([])
        self.refresh_notes_list()
