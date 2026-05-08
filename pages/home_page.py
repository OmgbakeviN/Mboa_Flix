import tkinter as tk
from config import COLORS, APP_NAME
from components.primary_button import PrimaryButton


class HomePage(tk.Frame):
    def __init__(self, master, user=None, on_logout=None):
        super().__init__(master, bg=COLORS["background"])
        self.user = user
        self.on_logout = on_logout

        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["background"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            container,
            text=f"{APP_NAME} Home",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 34, "bold")
        )
        title.pack(pady=(0, 15))

        subtitle = tk.Label(
            container,
            text="Waiting for design...",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Arial", 16)
        )
        subtitle.pack(pady=(0, 25))

        if self.user:
            user_label = tk.Label(
                container,
                text=f"Signed in as {self.user['email']}",
                bg=COLORS["background"],
                fg=COLORS["muted"],
                font=("Arial", 11)
            )
            user_label.pack(pady=(0, 25))

        PrimaryButton(
            container,
            text="Log Out",
            variant="secondary",
            command=self.on_logout
        ).pack()