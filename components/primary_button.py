import tkinter as tk
from config import COLORS


class PrimaryButton(tk.Button):
    def __init__(self, master, text, command=None, variant="primary", **kwargs):
        if variant == "primary":
            bg = COLORS["primary"]
            active_bg = COLORS["primary_hover"]
        else:
            bg = COLORS["secondary"]
            active_bg = COLORS["surface_light"]

        super().__init__(
            master,
            text=text,
            command=command,
            bg=bg,
            fg=COLORS["text"],
            activebackground=active_bg,
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 12, "bold"),
            padx=22,
            pady=10,
            **kwargs
        )