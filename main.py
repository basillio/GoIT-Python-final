import tkinter as tk
from tkinter import ttk, messagebox
import sys
from phonebook import Phonebook
from notes import NotesManager
from ui import PhonebookUI
from cli import PhonebookCLI


def show_mode_selection():
    """Show mode selection dialog with numbered options"""
    print("\n" + "="*60)
    print("Assistant Phonebook - Mode Selection")
    print("="*60)
    print("\nSelect mode:")
    print("  1. GUI Mode - Interactive graphical interface")
    print("  2. CLI Mode - Command-line interface")
    print("\nEnter your choice (1 or 2): ", end="")

    while True:
        choice = input().strip()
        if choice == "1":
            return "ui"
        elif choice == "2":
            return "cli"
        else:
            print("Invalid choice. Please enter 1 or 2: ", end="")


def main():
    # Show mode selection
    mode = show_mode_selection()

    if mode == "ui":
        # Launch GUI mode
        root = tk.Tk()
        root.title("Assistant Phonebook")
        root.geometry("1100x750")

        phonebook = Phonebook("contacts.json")
        notes_manager = NotesManager("notes.json")
        app = PhonebookUI(root, phonebook, notes_manager)

        root.mainloop()

    elif mode == "cli":
        # Launch CLI mode
        cli = PhonebookCLI()
        cli.run()
    else:
        print("No mode selected. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()

