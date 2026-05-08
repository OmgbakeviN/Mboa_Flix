import tkinter as tk
from config import COLORS


class TextInput(tk.Frame):
    def __init__(self, master, label, show=None):
        super().__init__(master, bg=COLORS["surface"])

        self.label = tk.Label(
            self,
            text=label,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 5))

        self.entry = tk.Entry(
            self,
            bg=COLORS["surface_light"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Arial", 12),
            show=show
        )
        self.entry.pack(fill="x", ipady=10)

    def get(self):
        return self.entry.get().strip()

    def focus(self):
        self.entry.focus_set()