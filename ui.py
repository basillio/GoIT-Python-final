import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

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
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Common search frame at top
        search_frame = ttk.LabelFrame(main_frame, text="Global Search", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search All:").pack(side=tk.LEFT, padx=5)
        self.global_search_var = tk.StringVar()
        self.global_search_var.trace("w", self.on_global_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.global_search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(search_frame, text="Clear", command=self.clear_global_search).pack(side=tk.LEFT, padx=5)

        # Results frame
        self.global_results_var = tk.StringVar(value="Ready")
        ttk.Label(search_frame, textvariable=self.global_results_var, foreground="blue").pack(side=tk.LEFT, padx=5)

        # Initialize dropdown window (will be created on demand)
        self.search_dropdown_window = None
        self.search_results_data = []

        # Birthday section
        birthday_frame = ttk.LabelFrame(main_frame, text="Upcoming Birthdays", padding=10)
        birthday_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(birthday_frame, text="Days ahead (0-365):").pack(side=tk.LEFT, padx=5)
        self.birthday_days_var = tk.StringVar(value="30")
        birthday_entry = ttk.Entry(birthday_frame, textvariable=self.birthday_days_var, width=10)
        birthday_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(birthday_frame, text="Show Birthdays", command=self.show_upcoming_birthdays).pack(side=tk.LEFT, padx=5)

        # Birthday results frame
        self.birthday_results_var = tk.StringVar(value="")
        ttk.Label(birthday_frame, textvariable=self.birthday_results_var, foreground="darkgreen").pack(side=tk.LEFT, padx=5)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        ttk.Button(search_frame, text="Clear", command=self.clear_global_search).pack(side=tk.LEFT, padx=5)

        # Results frame
        self.global_results_var = tk.StringVar(value="Ready")
        ttk.Label(search_frame, textvariable=self.global_results_var, foreground="blue").pack(side=tk.LEFT, padx=5)

        # Initialize dropdown window (will be created on demand)
        self.search_dropdown_window = None
        self.search_results_data = []

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
        # Button frame (removed search input)
        button_frame = ttk.Frame(self.contacts_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

        ttk.Button(button_frame, text="New Contact", command=self.new_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Settings", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(button_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.RIGHT, padx=5)

        # Main content frame
        content_frame = ttk.Frame(self.contacts_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10)

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
        card_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)

        self.card_text = tk.Text(card_frame, height=10, width=40, state=tk.DISABLED, font=("Courier", 8))
        self.card_text.pack(fill=tk.BOTH, expand=True)

        # Contact details form
        details_frame = ttk.LabelFrame(right_frame, text="Contact Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Name
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: John Doe", font=("Arial", 8), foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=5)

        # Phone 1
        ttk.Label(details_frame, text="Phone 1:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.phone1_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.phone1_var, width=30).grid(row=1, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: +1 (555) 123-4567", font=("Arial", 8), foreground="gray").grid(row=1, column=2, sticky=tk.W, padx=5)

        # Phone 2
        ttk.Label(details_frame, text="Phone 2:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.phone2_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.phone2_var, width=30).grid(row=2, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: 555-1234", font=("Arial", 8), foreground="gray").grid(row=2, column=2, sticky=tk.W, padx=5)

        # Email
        ttk.Label(details_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.email_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.email_var, width=30).grid(row=3, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: john@example.com", font=("Arial", 8), foreground="gray").grid(row=3, column=2, sticky=tk.W, padx=5)

        # Birthday
        ttk.Label(details_frame, text="Birthday:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.birthday_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.birthday_var, width=30).grid(row=4, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: 1990-05-15", font=("Arial", 8), foreground="gray").grid(row=4, column=2, sticky=tk.W, padx=5)

        # Tags
        ttk.Label(details_frame, text="Tags:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.tags_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.tags_var, width=30).grid(row=5, column=1, sticky=tk.EW, pady=3)
        ttk.Label(details_frame, text="Example: friend, work", font=("Arial", 8), foreground="gray").grid(row=5, column=2, sticky=tk.W, padx=5)

        # Note
        ttk.Label(details_frame, text="Note:").grid(row=6, column=0, sticky=tk.NW, pady=3)
        self.note_text = tk.Text(details_frame, height=4, width=30)
        self.note_text.grid(row=6, column=1, columnspan=2, sticky=tk.EW, pady=3)

        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        details_frame.columnconfigure(1, weight=1)

    def setup_notes_tab(self):
        """Setup the Notes tab"""
        # Button frame (removed search input)
        button_frame = ttk.Frame(self.notes_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

        ttk.Button(button_frame, text="New Note", command=self.new_note).pack(side=tk.LEFT, padx=5)

        # Status label
        self.notes_status_var = tk.StringVar(value="Ready")
        ttk.Label(button_frame, textvariable=self.notes_status_var, foreground="blue").pack(side=tk.RIGHT, padx=5)

        # Main content frame
        content_frame = ttk.Frame(self.notes_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Left side - notes list with filter
        left_frame = ttk.LabelFrame(content_frame, text="Notes List", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Tag filter frame with dropdown
        filter_frame = ttk.LabelFrame(left_frame, text="Filter by Tags", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        # Button to show/hide dropdown
        ttk.Label(filter_frame, text="Select Tags:").pack(side=tk.LEFT, padx=5)
        self.tag_filter_button = ttk.Button(filter_frame, text="Tags v", command=self.toggle_tag_dropdown)
        self.tag_filter_button.pack(side=tk.LEFT, padx=5)

        # Label to show selected tags
        self.selected_tags_var = tk.StringVar(value="All Tags")
        ttk.Label(filter_frame, textvariable=self.selected_tags_var, foreground="blue").pack(side=tk.LEFT, padx=5)

        # Dropdown frame (initially hidden) - fixed width to match notes list, half height
        self.dropdown_frame = tk.Frame(left_frame, bg="white", relief=tk.SUNKEN, bd=1, height=200, width=250)
        self.dropdown_frame.pack_propagate(False)
        self.dropdown_visible = False

        # Buttons frame at bottom - positioned first so it stays visible
        button_frame = tk.Frame(self.dropdown_frame, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Confirm", command=self.apply_tag_filter).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_all_tags).pack(side=tk.LEFT, padx=2)

        # Scrollable checkboxes frame
        self.tag_canvas = tk.Canvas(self.dropdown_frame, bg="white", highlightthickness=0)
        self.tag_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(self.dropdown_frame, orient=tk.VERTICAL, command=self.tag_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.checkbox_frame = tk.Frame(self.tag_canvas, bg="white")
        self.tag_canvas.create_window((0, 0), window=self.checkbox_frame, anchor=tk.NW)
        self.tag_canvas.configure(yscrollcommand=scrollbar.set)

        self.tag_checkboxes = {}
        self.tag_vars = {}

        # Notes treeview with columns
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_treeview = ttk.Treeview(tree_frame, columns=("Title", "Tags"),
                                           show="headings", height=25, yscrollcommand=scrollbar.set)
        self.notes_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.notes_treeview.yview)

        # Define columns
        self.notes_treeview.column("Title", width=150, anchor=tk.W)
        self.notes_treeview.column("Tags", width=100, anchor=tk.W)
        self.notes_treeview.heading("Title", text="Title", command=lambda: self.sort_notes_by_column("Title"))
        self.notes_treeview.heading("Tags", text="Tags", command=lambda: self.sort_notes_by_column("Tags"))

        self.notes_treeview.bind('<<TreeviewSelect>>', self.on_note_select)

        # Store note IDs for treeview items
        self.notes_tree_ids = {}

        # Right side - note details
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Note details form
        details_frame = ttk.LabelFrame(right_frame, text="Note Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(details_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.note_title_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.note_title_var, width=30).grid(row=0, column=1, sticky=tk.EW, pady=5)
        ttk.Label(details_frame, text="Example: 2026-05-28 14:30", font=("Arial", 8), foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=5)

        # Note text
        ttk.Label(details_frame, text="Note:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.note_content_text = tk.Text(details_frame, height=10, width=40)
        self.note_content_text.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)

        # Tags
        ttk.Label(details_frame, text="Tags:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.note_tags_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.note_tags_var, width=30).grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Label(details_frame, text="Example: important, work", font=("Arial", 8), foreground="gray").grid(row=2, column=2, sticky=tk.W, padx=5)

        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_note_form).pack(side=tk.LEFT, padx=5)

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
        tags_str = self.tags_var.get()
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

        is_valid, error_msg = self.phonebook.validate_contact(name, phone1, phone2, email, birthday, tags_str)
        if not is_valid:
            formatted_error = self._format_error_message(error_msg)
            messagebox.showwarning("Validation Error", formatted_error)
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

    def toggle_tag_dropdown(self):
        """Toggle dropdown visibility"""
        if self.dropdown_visible:
            self.dropdown_frame.pack_forget()
            self.dropdown_visible = False
        else:
            self.update_tag_dropdown_list()
            self.dropdown_frame.pack(fill=tk.X, pady=(0, 5), after=self.tag_filter_button.master)
            self.dropdown_visible = True
            self.root.bind("<Button-1>", self.on_click_outside_dropdown)

    def on_click_outside_dropdown(self, event):
        """Close dropdown when clicking outside"""
        if self.dropdown_visible:
            if not self.is_click_inside_dropdown(event):
                self.dropdown_frame.pack_forget()
                self.dropdown_visible = False
                self.root.unbind("<Button-1>")

    def is_click_inside_dropdown(self, event):
        """Check if click is inside dropdown"""
        x = event.x_root
        y = event.y_root

        dropdown_x1 = self.dropdown_frame.winfo_rootx()
        dropdown_y1 = self.dropdown_frame.winfo_rooty()
        dropdown_x2 = dropdown_x1 + self.dropdown_frame.winfo_width()
        dropdown_y2 = dropdown_y1 + self.dropdown_frame.winfo_height()

        button_x1 = self.tag_filter_button.winfo_rootx()
        button_y1 = self.tag_filter_button.winfo_rooty()
        button_x2 = button_x1 + self.tag_filter_button.winfo_width()
        button_y2 = button_y1 + self.tag_filter_button.winfo_height()

        return (dropdown_x1 <= x <= dropdown_x2 and dropdown_y1 <= y <= dropdown_y2) or \
               (button_x1 <= x <= button_x2 and button_y1 <= y <= button_y2)

    def update_tag_dropdown_list(self):
        """Update dropdown with all tags"""
        all_tags = self.notes_manager.get_all_tags()

        # Get currently selected tags from label
        current_selection = self.selected_tags_var.get()
        selected_tags_list = []
        if current_selection != "All Tags":
            # Parse selected tags from label (remove +N count)
            tags_text = current_selection.split(" +")[0]
            selected_tags_list = [tag.strip() for tag in tags_text.split(",")]

        # Clear existing checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.tag_checkboxes = {}
        self.tag_vars = {}

        # Add "All Tags" option
        all_tags_var = tk.BooleanVar(value=False)
        self.tag_vars["__all__"] = all_tags_var
        ttk.Checkbutton(self.checkbox_frame, text="All Tags", variable=all_tags_var,
                       command=self.on_tag_checkbox_change).pack(anchor=tk.W, pady=2)

        # Add separator
        ttk.Separator(self.checkbox_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)

        # Add checkboxes for each tag
        for tag in sorted(all_tags):
            # Set to True if tag is already selected
            is_selected = tag in selected_tags_list
            var = tk.BooleanVar(value=is_selected)
            self.tag_vars[tag] = var
            checkbox = ttk.Checkbutton(self.checkbox_frame, text=tag, variable=var,
                                      command=self.on_tag_checkbox_change)
            checkbox.pack(anchor=tk.W, pady=2)
            self.tag_checkboxes[tag] = checkbox

        # Update canvas scroll region
        self.checkbox_frame.update_idletasks()
        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))

    def on_tag_checkbox_change(self):
        """Handle checkbox changes"""
        if self.tag_vars.get("__all__", tk.BooleanVar()).get():
            for tag, var in self.tag_vars.items():
                if tag != "__all__":
                    var.set(False)
        else:
            self.tag_vars["__all__"].set(False)

    def apply_tag_filter(self):
        """Apply tag filter and close dropdown"""
        selected_tags = [tag for tag, var in self.tag_vars.items()
                       if tag != "__all__" and var.get()]

        if not selected_tags or self.tag_vars.get("__all__", tk.BooleanVar()).get():
            self.selected_tags_var.set("All Tags")
            self.refresh_notes_list()
        else:
            if len(selected_tags) <= 3:
                tags_display = ", ".join(selected_tags)
            else:
                tags_display = ", ".join(selected_tags[:3]) + f" +{len(selected_tags) - 3}"
            self.selected_tags_var.set(tags_display)

            filtered_notes = [note for note in self.notes_manager.notes
                            if any(tag in note.get('tags', []) for tag in selected_tags)]
            self.refresh_notes_list(filtered_notes)

        # Close dropdown after confirming
        self.dropdown_frame.pack_forget()
        self.dropdown_visible = False
        self.root.unbind("<Button-1>")

    def clear_all_tags(self):
        """Clear all tag selections"""
        for var in self.tag_vars.values():
            var.set(False)
        self.selected_tags_var.set("All Tags")
        self.refresh_notes_list()

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

    def display_all_notes_on_startup(self):
        """Display all notes on application startup"""
        all_notes = self.notes_manager.notes

        if not all_notes:
            return

        notes_text = "All Notes:\n\n"
        for i, note in enumerate(all_notes, 1):
            title = note.get('title', 'Untitled')
            note_content = note.get('note', '')[:100]
            tags = ", ".join(note.get('tags', []))

            notes_text += f"{i}. {title}\n"
            notes_text += f"   Content: {note_content}...\n"
            if tags:
                notes_text += f"   Tags: {tags}\n"
            notes_text += "\n"

        self.root.after(500, lambda: messagebox.showinfo("All Notes", notes_text))

    def refresh_notes_list(self, notes=None):
        """Refresh the notes treeview"""
        # Clear treeview
        for item in self.notes_treeview.get_children():
            self.notes_treeview.delete(item)
        self.notes_tree_ids = {}

        if notes is None:
            notes = self.notes_manager.notes

        # Add notes to treeview
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
                self.display_note(note)

    def display_note(self, note):
        """Display note details in the form"""
        self.note_title_var.set(note.get("title", ""))
        self.note_content_text.delete("1.0", tk.END)
        self.note_content_text.insert("1.0", note.get("note", ""))
        self.note_tags_var.set(", ".join(note.get("tags", [])))

    def on_notes_search_change(self, *args):
        """Handle notes search input changes"""
        query = self.notes_search_var.get()
        results = self.notes_manager.search_notes(query)
        self.refresh_notes_list(results)
        self.clear_note_form()

    def clear_notes_search(self):
        """Clear notes search and show all notes"""
        self.notes_search_var.set("")
        self.refresh_notes_list()
        self.clear_note_form()

    def new_note(self):
        """Prepare form for new note"""
        self.current_note_id = None
        self.clear_note_form()
        self.notes_listbox.selection_clear(0, tk.END)

    def clear_note_form(self):
        """Clear all note form fields"""
        self.note_title_var.set("")
        self.note_content_text.delete("1.0", tk.END)
        self.note_tags_var.set("")
        self.current_note_id = None

    def save_note(self):
        """Save or update note"""
        title = self.note_title_var.get()
        note_text = self.note_content_text.get("1.0", tk.END).strip()
        tags_str = self.note_tags_var.get()
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

        is_valid, error_msg = self.notes_manager.validate_note(title, note_text, tags_str)
        if not is_valid:
            formatted_error = self._format_note_error_message(error_msg)
            messagebox.showwarning("Validation Error", formatted_error)
            return

        if self.current_note_id:
            if self.notes_manager.update_note(self.current_note_id, title, note_text, tags):
                self.notes_status_var.set("Note updated and saved to notes.json")
                messagebox.showinfo("Success", "Note updated successfully!")
                self.refresh_notes_list()
                self.clear_note_form()
            else:
                messagebox.showerror("Error", "Failed to update note!")
        else:
            if self.notes_manager.add_note(title, note_text, tags):
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

    def on_global_search_change(self, *args):
        """Handle global search input changes across all tabs"""
        search_term = self.global_search_var.get().strip()

        if not search_term:
            self.global_results_var.set("Ready")
            self.close_search_dropdown()
            return

        # Search contacts
        contacts_results = self.phonebook.search_contacts(search_term)

        # Search notes
        notes_results = self.notes_manager.search_notes(search_term)

        # Format results display
        contact_count = len(contacts_results)
        notes_count = len(notes_results)

        if contact_count == 0 and notes_count == 0:
            self.global_results_var.set("No results found")
            self.close_search_dropdown()
            return

        result_text = []
        if contact_count > 0:
            result_text.append(f"{contact_count} Contact{'s' if contact_count != 1 else ''}")
        if notes_count > 0:
            result_text.append(f"{notes_count} Note{'s' if notes_count != 1 else ''}")

        self.global_results_var.set(" | ".join(result_text) + " found")

        # Prepare results data
        self.search_results_data = []

        # Add contacts to results
        for contact in contacts_results:
            display_text = f"[Contact] {contact.get('name', 'Unknown')}"
            if contact.get('phone'):
                display_text += f" - {contact['phone']}"
            self.search_results_data.append(('contact', contact, display_text))

        # Add notes to results
        for note in notes_results:
            display_text = f"[Note] {note.get('title', 'Untitled')}"
            self.search_results_data.append(('note', note, display_text))

        # Show dropdown
        self.show_search_dropdown()

    def show_search_dropdown(self):
        """Show floating dropdown window with search results"""
        # Close existing dropdown if any
        self.close_search_dropdown()

        # Create floating window
        self.search_dropdown_window = tk.Toplevel(self.root)
        self.search_dropdown_window.wm_overrideredirect(True)
        self.search_dropdown_window.attributes('-topmost', True)

        # Create listbox in dropdown first to get proper height
        item_count = min(len(self.search_results_data), 8)
        self.search_results_listbox = tk.Listbox(
            self.search_dropdown_window,
            font=("Arial", 9),
            bg="white",
            relief=tk.SUNKEN,
            bd=1,
            height=item_count
        )
        self.search_results_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate listbox
        for result_type, result_data, display_text in self.search_results_data:
            self.search_results_listbox.insert(tk.END, display_text)

        # Update to get proper dimensions
        self.search_dropdown_window.update_idletasks()
        self.search_entry.update_idletasks()

        # Position dropdown below search entry
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 2
        width = self.search_entry.winfo_width()
        height = self.search_results_listbox.winfo_reqheight()

        self.search_dropdown_window.geometry(f"{width}x{height}+{x}+{y}")

        # Bind events
        self.search_results_listbox.bind('<<ListboxSelect>>', self.on_search_result_select)
        self.search_dropdown_window.bind('<FocusOut>', self.on_search_dropdown_focus_out)
        self.root.bind('<Button-1>', self.on_root_click)

    def on_search_result_select(self, event):
        """Handle search result selection from dropdown"""
        selection = self.search_results_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        result_type, result_data, _ = self.search_results_data[index]

        if result_type == 'contact':
            # Switch to Contacts tab
            self.notebook.select(0)
            self.current_contact_id = result_data.get('id')

            # Display contact details
            self.display_contact(result_data)
            self.update_card_preview(result_data)

            # Highlight in contacts list
            self.refresh_contacts_list()
            for i, contact_id in enumerate(self.contact_ids):
                if contact_id == self.current_contact_id:
                    self.contacts_listbox.selection_clear(0, tk.END)
                    self.contacts_listbox.selection_set(i)
                    self.contacts_listbox.see(i)
                    break

        elif result_type == 'note':
            # Switch to Notes tab
            self.notebook.select(1)
            self.current_note_id = result_data.get('id')

            # Display note details
            self.display_note(result_data)

            # Highlight in notes treeview
            self.refresh_notes_list()
            for tree_item_id, note_id in self.notes_tree_ids.items():
                if note_id == self.current_note_id:
                    self.notes_treeview.selection_set(tree_item_id)
                    self.notes_treeview.see(tree_item_id)
                    break

        # Close dropdown
        self.close_search_dropdown()

    def on_search_dropdown_focus_out(self, event):
        """Close dropdown when it loses focus"""
        self.close_search_dropdown()

    def on_root_click(self, event):
        """Close dropdown when clicking outside of it"""
        if self.search_dropdown_window:
            if not self.is_point_in_widget(event.x_root, event.y_root, self.search_dropdown_window):
                self.close_search_dropdown()

    def is_point_in_widget(self, x, y, widget):
        """Check if point is within widget bounds"""
        try:
            x1 = widget.winfo_rootx()
            y1 = widget.winfo_rooty()
            x2 = x1 + widget.winfo_width()
            y2 = y1 + widget.winfo_height()
            return x1 <= x <= x2 and y1 <= y <= y2
        except:
            return False

    def close_search_dropdown(self):
        """Close the search dropdown window"""
        if self.search_dropdown_window:
            try:
                self.search_dropdown_window.destroy()
            except:
                pass
            self.search_dropdown_window = None

    def clear_global_search(self):
        """Clear global search and reset results"""
        self.global_search_var.set("")
        self.global_results_var.set("Ready")
        self.close_search_dropdown()

    def show_upcoming_birthdays(self):
        """Show contacts with birthdays within specified days"""
        try:
            days_input = self.birthday_days_var.get().strip()
            if not days_input:
                self.birthday_results_var.set("Please enter number of days")
                return

            days = int(days_input)
            if days < 0 or days > 365:
                self.birthday_results_var.set("Days must be between 0-365")
                return

            today = datetime.now().date()
            upcoming = []

            for contact in self.phonebook.contacts:
                birthday_str = contact.get("birthday", "")
                if not birthday_str:
                    continue

                try:
                    birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                    # Calculate next birthday
                    next_birthday = birthday.replace(year=today.year)
                    if next_birthday < today:
                        next_birthday = next_birthday.replace(year=today.year + 1)

                    days_until = (next_birthday - today).days

                    if 0 <= days_until <= days:
                        upcoming.append((contact.get("name", "Unknown"), days_until, birthday_str))
                except:
                    continue

            if upcoming:
                # Sort by days until birthday
                upcoming.sort(key=lambda x: x[1])
                result_text = f"{len(upcoming)} birthday(s): "
                details = []
                for name, days_until, birthday in upcoming:
                    if days_until == 0:
                        details.append(f"{name} (TODAY)")
                    else:
                        details.append(f"{name} ({days_until}d)")
                result_text += " | ".join(details)
                self.birthday_results_var.set(result_text)
            else:
                self.birthday_results_var.set("No birthdays in next " + days_input + " days")

        except ValueError:
            self.birthday_results_var.set("Invalid input - enter number 0-365")
        except Exception as e:
            self.birthday_results_var.set("Error: " + str(e))