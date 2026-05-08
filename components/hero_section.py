import tkinter as tk

from config import COLORS
from components.primary_button import PrimaryButton


class HeroSection(tk.Frame):
    def __init__(self, master, movie=None, on_watch=None, on_details=None):
        super().__init__(master, bg="#050505")

        self.movie = movie or {}
        self.on_watch = on_watch
        self.on_details = on_details

        self._build_ui()
        self.set_movie(self.movie)

    def _build_ui(self):
        self.category_label = tk.Label(
            self,
            text="",
            bg="#050505",
            fg=COLORS["primary"],
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.category_label.pack(fill="x", pady=(0, 8))

        self.title_label = tk.Label(
            self,
            text="",
            bg="#050505",
            fg=COLORS["text"],
            font=("Arial", 34, "bold"),
            anchor="w",
            justify="left"
        )
        self.title_label.pack(fill="x")

        self.meta_label = tk.Label(
            self,
            text="",
            bg="#050505",
            fg=COLORS["muted"],
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.meta_label.pack(fill="x", pady=(8, 10))

        self.description_label = tk.Label(
            self,
            text="",
            bg="#050505",
            fg=COLORS["text"],
            font=("Arial", 11),
            wraplength=540,
            justify="left",
            anchor="w"
        )
        self.description_label.pack(fill="x", pady=(0, 18))

        button_row = tk.Frame(self, bg="#050505")
        button_row.pack(fill="x")

        self.watch_button = PrimaryButton(
            button_row,
            text="▶ Watch Now",
            command=self._watch
        )
        self.watch_button.pack(side="left", padx=(0, 10))

        self.details_button = PrimaryButton(
            button_row,
            text="Details",
            variant="secondary",
            command=self._details
        )
        self.details_button.pack(side="left", padx=(0, 10))

        self.my_list_button = PrimaryButton(
            button_row,
            text="＋ My List",
            variant="secondary",
            command=lambda: None
        )
        self.my_list_button.pack(side="left")

    def set_movie(self, movie):
        self.movie = movie or {}

        if not self.movie:
            self.category_label.config(text="")
            self.title_label.config(text="No movie selected")
            self.meta_label.config(text="")
            self.description_label.config(text="")
            return

        tags = self.movie.get("tags", [])
        tag_text = "  •  ".join(tags[:3]) if tags else self.movie.get("category", "")

        rating = self.movie.get("rating", "N/A")
        year = self.movie.get("year", "")
        duration = self.movie.get("duration", "")
        match = self.movie.get("match", "")

        self.category_label.config(text=tag_text.upper())
        self.title_label.config(text=self.movie.get("title", "Untitled"))

        self.meta_label.config(
            text=f"★ {rating}    {match} Match    {year}    {duration}"
        )

        self.description_label.config(
            text=self.movie.get("description", "")
        )

    def _watch(self):
        if callable(self.on_watch):
            self.on_watch(self.movie)

    def _details(self):
        if callable(self.on_details):
            self.on_details(self.movie)