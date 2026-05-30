import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class SearchComponent:
    def __init__(self, parent, on_search_change, on_clear):
        self.parent = parent
        self.on_search_change = on_search_change
        self.on_clear = on_clear
        self.search_var = tk.StringVar()
        self.results_var = tk.StringVar(value="Ready")
        self.dropdown_window = None
        self.results_data = []
        self.results_listbox = None
        self.search_entry = None
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Global Search", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Search All:").pack(side=tk.LEFT, padx=5)
        self.search_var.trace("w", lambda *args: self.on_search_change())
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(frame, text="Clear", command=self.on_clear).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, textvariable=self.results_var, foreground="blue").pack(side=tk.LEFT, padx=5)

    def get_value(self):
        return self.search_var.get().strip()

    def set_results_text(self, text):
        self.results_var.set(text)

    def show_dropdown(self, results_data):
        self.results_data = results_data
        self.close_dropdown()

        self.dropdown_window = tk.Toplevel(self.parent.winfo_toplevel())
        self.dropdown_window.wm_overrideredirect(True)
        self.dropdown_window.attributes('-topmost', True)

        item_count = min(len(results_data), 8)
        self.results_listbox = tk.Listbox(
            self.dropdown_window,
            font=("Arial", 9),
            bg="white",
            relief=tk.SUNKEN,
            bd=1,
            height=item_count
        )
        self.results_listbox.pack(fill=tk.BOTH, expand=True)

        for result_type, result_data, display_text in results_data:
            self.results_listbox.insert(tk.END, display_text)

        self.dropdown_window.update_idletasks()
        self.search_entry.update_idletasks()

        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 2
        width = self.search_entry.winfo_width()
        height = self.results_listbox.winfo_reqheight()

        self.dropdown_window.geometry(f"{width}x{height}+{x}+{y}")

    def close_dropdown(self):
        if self.dropdown_window:
            try:
                self.dropdown_window.destroy()
            except:
                pass
            self.dropdown_window = None

    def clear(self):
        self.search_var.set("")
        self.results_var.set("Ready")
        self.close_dropdown()


class BirthdayComponent:
    def __init__(self, parent, on_show_birthdays):
        self.parent = parent
        self.on_show_birthdays = on_show_birthdays
        self.days_var = tk.StringVar(value="30")
        self.results_var = tk.StringVar(value="")
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Upcoming Birthdays", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Days ahead (0-365):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame, textvariable=self.days_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Show Birthdays", command=self.on_show_birthdays).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, textvariable=self.results_var, foreground="darkgreen").pack(side=tk.LEFT, padx=5)

    def get_days(self):
        try:
            return int(self.days_var.get().strip())
        except ValueError:
            return None

    def set_results(self, text):
        self.results_var.set(text)


class ContactFormComponent:
    def __init__(self, parent):
        self.parent = parent
        self.name_var = tk.StringVar()
        self.phone1_var = tk.StringVar()
        self.phone2_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.birthday_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        self.note_text = None
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Contact Details", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Name:", self.name_var, "Example: John Doe", 0),
            ("Phone 1:", self.phone1_var, "Example: +1 (555) 123-4567", 1),
            ("Phone 2:", self.phone2_var, "Example: 555-1234", 2),
            ("Email:", self.email_var, "Example: john@example.com", 3),
            ("Birthday:", self.birthday_var, "Example: 1990-05-15", 4),
            ("Tags:", self.tags_var, "Example: friend, work", 5),
        ]

        for label, var, example, row in fields:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            ttk.Entry(frame, textvariable=var, width=30).grid(row=row, column=1, sticky=tk.EW, pady=3)
            ttk.Label(frame, text=example, font=("Arial", 8), foreground="gray").grid(row=row, column=2, sticky=tk.W, padx=5)

        ttk.Label(frame, text="Note:").grid(row=6, column=0, sticky=tk.NW, pady=3)
        self.note_text = tk.Text(frame, height=8, width=30)
        self.note_text.grid(row=6, column=1, columnspan=2, sticky=tk.EW, pady=3)

        frame.columnconfigure(1, weight=1)

    def get_data(self):
        return {
            'name': self.name_var.get(),
            'phone1': self.phone1_var.get(),
            'phone2': self.phone2_var.get(),
            'email': self.email_var.get(),
            'birthday': self.birthday_var.get(),
            'tags': self.tags_var.get(),
            'note': self.note_text.get("1.0", tk.END).strip()
        }

    def set_data(self, contact):
        self.name_var.set(contact.get("name", ""))
        self.phone1_var.set(contact.get("phone1", ""))
        self.phone2_var.set(contact.get("phone2", ""))
        self.email_var.set(contact.get("email", ""))
        self.birthday_var.set(contact.get("birthday", ""))
        self.tags_var.set(", ".join(contact.get("tags", [])))
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", contact.get("note", ""))

    def clear(self):
        self.name_var.set("")
        self.phone1_var.set("")
        self.phone2_var.set("")
        self.email_var.set("")
        self.birthday_var.set("")
        self.tags_var.set("")
        self.note_text.delete("1.0", tk.END)


class ContactCardComponent:
    def __init__(self, parent):
        self.parent = parent
        self.card_text = None
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Contact Card Preview", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10), ipady=5)

        self.card_text = tk.Text(frame, height=15, width=40, state=tk.DISABLED, font=("Courier", 8))
        self.card_text.pack(fill=tk.BOTH, expand=True)

    def update(self, contact):
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
            for line in note_lines[:10]:
                truncated = truncate(line, 32)
                self.card_text.insert(tk.END, f"║ {truncated:<32}   ║\n")
            if len(note_lines) > 10:
                self.card_text.insert(tk.END, "║ (... more notes ...)            ║\n")
        else:
            self.card_text.insert(tk.END, "║ (no notes)                       ║\n")

        self.card_text.insert(tk.END, "╚════════════════════════════════════╝")
        self.card_text.config(state=tk.DISABLED)


class NoteFormComponent:
    def __init__(self, parent):
        self.parent = parent
        self.title_var = tk.StringVar()
        self.content_text = None
        self.tags_var = tk.StringVar()
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Note Details", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.title_var, width=30).grid(row=0, column=1, sticky=tk.EW, pady=5)
        ttk.Label(frame, text="Example: 2026-05-28 14:30", font=("Arial", 8), foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=5)

        ttk.Label(frame, text="Note:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.content_text = tk.Text(frame, height=10, width=40)
        self.content_text.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Tags:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.tags_var, width=30).grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Label(frame, text="Example: important, work", font=("Arial", 8), foreground="gray").grid(row=2, column=2, sticky=tk.W, padx=5)

        frame.columnconfigure(1, weight=1)

    def get_data(self):
        return {
            'title': self.title_var.get(),
            'content': self.content_text.get("1.0", tk.END).strip(),
            'tags': self.tags_var.get()
        }

    def set_data(self, note):
        self.title_var.set(note.get("title", ""))
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", note.get("note", ""))
        self.tags_var.set(", ".join(note.get("tags", [])))

    def clear(self):
        self.title_var.set("")
        self.content_text.delete("1.0", tk.END)
        self.tags_var.set("")


class TagFilterComponent:
    def __init__(self, parent, on_apply, on_clear):
        self.parent = parent
        self.on_apply = on_apply
        self.on_clear = on_clear
        self.selected_tags_var = tk.StringVar(value="All Tags")
        self.dropdown_visible = False
        self.dropdown_frame = None
        self.tag_canvas = None
        self.checkbox_frame = None
        self.tag_vars = {}
        self.tag_filter_button = None
        self.build()

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Filter by Tags", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame, text="Select Tags:").pack(side=tk.LEFT, padx=5)
        self.tag_filter_button = ttk.Button(frame, text="Tags v", command=self.toggle)
        self.tag_filter_button.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame, textvariable=self.selected_tags_var, foreground="blue").pack(side=tk.LEFT, padx=5)

        self.dropdown_frame = tk.Frame(self.parent, bg="white", relief=tk.SUNKEN, bd=1, height=200, width=250)
        self.dropdown_frame.pack_propagate(False)

        button_frame = tk.Frame(self.dropdown_frame, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Confirm", command=self.apply).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        self.tag_canvas = tk.Canvas(self.dropdown_frame, bg="white", highlightthickness=0)
        self.tag_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(self.dropdown_frame, orient=tk.VERTICAL, command=self.tag_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.checkbox_frame = tk.Frame(self.tag_canvas, bg="white")
        self.tag_canvas.create_window((0, 0), window=self.checkbox_frame, anchor=tk.NW)
        self.tag_canvas.configure(yscrollcommand=scrollbar.set)

    def toggle(self):
        if self.dropdown_visible:
            self.dropdown_frame.pack_forget()
            self.dropdown_visible = False
        else:
            self.update_list()
            self.dropdown_frame.pack(fill=tk.X, pady=(0, 5), after=self.tag_filter_button.master)
            self.dropdown_visible = True

    def update_list(self, all_tags=None, selected_tags=None):
        if all_tags is None:
            all_tags = []
        if selected_tags is None:
            selected_tags = []

        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.tag_vars = {}

        all_tags_var = tk.BooleanVar(value=False)
        self.tag_vars["__all__"] = all_tags_var
        ttk.Checkbutton(self.checkbox_frame, text="All Tags", variable=all_tags_var,
                       command=self.on_tag_change).pack(anchor=tk.W, pady=2)

        ttk.Separator(self.checkbox_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)

        for tag in sorted(all_tags):
            is_selected = tag in selected_tags
            var = tk.BooleanVar(value=is_selected)
            self.tag_vars[tag] = var
            ttk.Checkbutton(self.checkbox_frame, text=tag, variable=var,
                           command=self.on_tag_change).pack(anchor=tk.W, pady=2)

        self.checkbox_frame.update_idletasks()
        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))

    def on_tag_change(self):
        if self.tag_vars.get("__all__", tk.BooleanVar()).get():
            for tag, var in self.tag_vars.items():
                if tag != "__all__":
                    var.set(False)
        else:
            self.tag_vars["__all__"].set(False)

    def get_selected(self):
        return [tag for tag, var in self.tag_vars.items()
                if tag != "__all__" and var.get()]

    def apply(self):
        self.on_apply(self.get_selected())
        self.dropdown_frame.pack_forget()
        self.dropdown_visible = False

    def clear_all(self):
        for var in self.tag_vars.values():
            var.set(False)
        self.selected_tags_var.set("All Tags")
        self.on_clear()

    def set_selected_display(self, tags):
        if not tags:
            self.selected_tags_var.set("All Tags")
        else:
            if len(tags) <= 3:
                self.selected_tags_var.set(", ".join(tags))
            else:
                self.selected_tags_var.set(", ".join(tags[:3]) + f" +{len(tags) - 3}")
