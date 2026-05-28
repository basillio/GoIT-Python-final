import tkinter as tk
from tkinter import ttk, messagebox
from phonebook import Phonebook
from ui import PhonebookUI

def main():
    root = tk.Tk()
    root.title("Assistant Phonebook")
    root.geometry("900x700")

    phonebook = Phonebook("contacts.json")
    app = PhonebookUI(root, phonebook)

    root.mainloop()

if __name__ == "__main__":
    main()
