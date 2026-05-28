import tkinter as tk
from tkinter import ttk, messagebox
from phonebook import Phonebook
from notes import NotesManager
from ui import PhonebookUI

def main():
    root = tk.Tk()
    root.title("Assistant Phonebook")
    root.geometry("1100x750")

    phonebook = Phonebook("contacts.json")
    notes_manager = NotesManager("notes.json")
    app = PhonebookUI(root, phonebook, notes_manager)

    root.mainloop()

if __name__ == "__main__":
    main()
