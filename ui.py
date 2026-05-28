import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class PhonebookUI:
    def __init__(self, root, phonebook):
        self.root = root
        self.phonebook = phonebook
        self.current_contact_id = None
        self.contact_ids = []
        self.notification_days = [0, 1, 3, 7]
        self.load_settings()
        self.setup_ui()
        self.refresh_contacts_list()
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
        """Setup the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Top search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search Contacts", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="New Contact", command=self.new_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Settings", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(search_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.RIGHT, padx=5)

        # Main content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - contacts list
        left_frame = ttk.LabelFrame(content_frame, text="Contacts List", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Contacts listbox with scrollbar
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

        # Contact card preview
        card_frame = ttk.LabelFrame(right_frame, text="Contact Card Preview", padding=10)
        card_frame.pack(fill=tk.X, pady=(0, 10))

        self.card_text = tk.Text(card_frame, height=14, width=40, state=tk.DISABLED, font=("Courier", 8))
        self.card_text.pack(fill=tk.BOTH, expand=True)

        # Contact details form
        details_frame = ttk.LabelFrame(right_frame, text="Contact Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Name
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.EW, pady=5)

        # Phone 1
        ttk.Label(details_frame, text="Phone 1:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.phone1_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.phone1_var, width=30).grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Phone 2
        ttk.Label(details_frame, text="Phone 2:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone2_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.phone2_var, width=30).grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Email
        ttk.Label(details_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.email_var, width=30).grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Birthday
        ttk.Label(details_frame, text="Birthday:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.birthday_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.birthday_var, width=30).grid(row=4, column=1, sticky=tk.EW, pady=5)
        ttk.Label(details_frame, text="(YYYY-MM-DD)", font=("Arial", 8)).grid(row=4, column=2, sticky=tk.W, padx=5)

        # Tags
        ttk.Label(details_frame, text="Tags:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.tags_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.tags_var, width=30).grid(row=5, column=1, sticky=tk.EW, pady=5)
        ttk.Label(details_frame, text="(comma separated)", font=("Arial", 8)).grid(row=5, column=2, sticky=tk.W, padx=5)

        # Note
        ttk.Label(details_frame, text="Note:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.note_text = tk.Text(details_frame, height=5, width=30)
        self.note_text.grid(row=6, column=1, columnspan=2, sticky=tk.EW, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        details_frame.columnconfigure(1, weight=1)

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
                self.display_contact(contact)
                self.update_card_preview(contact)

    def display_contact(self, contact):
        """Display contact details in the form"""
        self.name_var.set(contact.get("name", ""))
        self.phone1_var.set(contact.get("phone1", ""))
        self.phone2_var.set(contact.get("phone2", ""))
        self.email_var.set(contact.get("email", ""))
        self.birthday_var.set(contact.get("birthday", ""))
        self.tags_var.set(", ".join(contact.get("tags", [])))
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", contact.get("note", ""))

    def update_card_preview(self, contact):
        """Update the contact card preview"""
        self.card_text.config(state=tk.NORMAL)
        self.card_text.delete("1.0", tk.END)

        name = contact.get('name', 'N/A')
        phone1 = contact.get('phone1', '')
        phone2 = contact.get('phone2', '')
        email = contact.get('email', '')
        birthday = contact.get('birthday', '')
        tags = ', '.join(contact.get('tags', []))
        note = contact.get('note', '')

        phone1_display = phone1 if phone1 else '(not set)'
        phone2_display = phone2 if phone2 else '(not set)'
        email_display = email if email else '(not set)'
        birthday_display = birthday if birthday else '(not set)'
        tags_display = tags if tags else '(no tags)'

        truncate = lambda s, l: (s[:l-3] + '...') if len(s) > l else s

        card_content = f"""╔════════════════════════════════════╗
║ {name[:32]:^32}   ║
╠════════════════════════════════════╣
║ CONTACT INFORMATION                ║
║ ────────────────────────────────── ║
║ Phone 1: {truncate(phone1_display, 24):<24}  ║
║ Phone 2: {truncate(phone2_display, 24):<24}  ║
║ Email: {truncate(email_display, 27):<27} ║
║ Birthday: {truncate(birthday_display, 23):<23}  ║
║ Tags: {truncate(tags_display, 28):<28} ║
╠════════════════════════════════════╣
║ NOTES:                             ║
"""
        self.card_text.insert("1.0", card_content)

        if note:
            note_lines = note.split('\n')
            for line in note_lines[:4]:
                truncated = truncate(line, 32)
                self.card_text.insert(tk.END, f"║ {truncated:<32}   ║\n")
            if len(note_lines) > 4:
                self.card_text.insert(tk.END, "║ (... more notes ...)            ║\n")
        else:
            self.card_text.insert(tk.END, "║ (no notes)                       ║\n")

        self.card_text.insert(tk.END, "╚════════════════════════════════════╝")
        self.card_text.config(state=tk.DISABLED)

    def on_search_change(self, *args):
        """Handle search input changes"""
        query = self.search_var.get()
        results = self.phonebook.search_contacts(query)
        self.refresh_contacts_list(results)
        self.clear_form()

    def clear_search(self):
        """Clear search and show all contacts"""
        self.search_var.set("")
        self.refresh_contacts_list()
        self.clear_form()

    def new_contact(self):
        """Prepare form for new contact"""
        self.current_contact_id = None
        self.clear_form()
        self.contacts_listbox.selection_clear(0, tk.END)

    def clear_form(self):
        """Clear all form fields"""
        self.name_var.set("")
        self.phone1_var.set("")
        self.phone2_var.set("")
        self.email_var.set("")
        self.birthday_var.set("")
        self.tags_var.set("")
        self.note_text.delete("1.0", tk.END)
        self.current_contact_id = None

    def save_contact(self):
        """Save or update contact"""
        name = self.name_var.get()
        phone1 = self.phone1_var.get()
        phone2 = self.phone2_var.get()
        email = self.email_var.get()
        birthday = self.birthday_var.get()
        note = self.note_text.get("1.0", tk.END).strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]

        if not name.strip():
            messagebox.showwarning("Validation", "Name is required!")
            return

        if self.current_contact_id:
            if self.phonebook.update_contact(self.current_contact_id, name, phone1, phone2,
                                            email, birthday, note, tags):
                self.status_var.set("Contact updated and saved to contacts.json")
                messagebox.showinfo("Success", "Contact updated successfully!")
                self.refresh_contacts_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update contact!")
        else:
            if self.phonebook.add_contact(name, phone1, phone2, email, birthday, note, tags):
                self.status_var.set("New contact added and saved to contacts.json")
                messagebox.showinfo("Success", "Contact added successfully!")
                self.refresh_contacts_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to add contact!")

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

        settings = {
            "notification_days": self.notification_days
        }

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
                        upcoming_birthdays.append(f"🎂 {name} - Birthday TODAY!")
                    else:
                        upcoming_birthdays.append(f"🎂 {name} - Birthday in {days_until} day(s)")
            except ValueError:
                continue

        if upcoming_birthdays:
            notification_text = "Upcoming Birthdays:\n\n" + "\n".join(upcoming_birthdays)
            self.root.after(100, lambda: messagebox.showinfo("Birthday Notifications", notification_text))
